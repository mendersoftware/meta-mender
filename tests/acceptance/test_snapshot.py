#!/usr/bin/python
# Copyright 2023 Northern.tech AS
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import re
import subprocess
import tempfile

import pytest

from utils.common import (
    determine_active_passive_part,
    get_ssh_common_args,
    version_is_minimum,
)


def get_ssh_args_mender_artifact(conn):
    common_args = get_ssh_common_args(conn)
    # mender-artifact prefixes each ssh argument with "-S"
    common_args = common_args.replace(" ", " -S ")
    # Prefix the first argument too
    return "-S " + common_args


def get_mender_snapshot_bin(bitbake_variables):
    if version_is_minimum(bitbake_variables, "mender-client", "4.0.0"):
        return "mender-snapshot"
    return "mender snapshot"


@pytest.mark.cross_platform
@pytest.mark.only_with_image("uefiimg", "sdimg", "biosimg", "gptimg")
@pytest.mark.usefixtures("setup_board", "bitbake_path")
@pytest.mark.min_mender_version("2.2.0")
class TestSnapshotStandalone:
    @pytest.mark.parametrize("compression", [("", ">"), ("-C gzip", "| gunzip -c >")])
    def test_basic_snapshot(self, compression, bitbake_variables, connection):
        try:
            (_, passive) = determine_active_passive_part(bitbake_variables, connection)

            # Wipe the inactive partition first.
            connection.run(f"dd if=/dev/zero of={passive} bs=1M count=100")

            # Dump what we currently have to the inactive partition.
            connection.run(
                f"{get_mender_snapshot_bin(bitbake_variables)} dump "
                + f"{compression[0]} {compression[1]} {passive}"
            )

            # Make sure this looks like a sane filesystem.
            connection.run(f"fsck.ext4 -p {passive}")

            # And that it can be mounted with actual content.
            connection.run(f"mount {passive} /mnt")
            connection.run("test -f /mnt/etc/passwd")

        finally:
            connection.run("umount /mnt || true")

    def test_snapshot_device_file(self, bitbake_variables, connection):
        try:
            (active, passive) = determine_active_passive_part(
                bitbake_variables, connection
            )

            # Wipe the inactive partition first.
            connection.run(f"dd if=/dev/zero of={passive} bs=1M count=100")

            # Dump what we currently have to the inactive partition, using
            # device file reference.
            connection.run(
                f"{get_mender_snapshot_bin(bitbake_variables)} dump "
                + f"--source {active} > {passive}"
            )

            # Make sure this looks like a sane filesystem.
            connection.run(f"fsck.ext4 -p {passive}")

            # And that it can be mounted with actual content.
            connection.run(f"mount {passive} /mnt")
            connection.run("test -f /mnt/etc/passwd")

        finally:
            connection.run("umount /mnt || true")

    def test_snapshot_inactive(self, bitbake_variables, connection):
        try:
            (_, passive) = determine_active_passive_part(bitbake_variables, connection)

            test_str = "TeSt StrIng!#"

            # Seed the initial part of the inactive partition with a test string
            connection.run(f"echo '{test_str}' | dd of={passive}")

            # Try to snapshot inactive partition, keeping the initial part, and
            # dumping the rest.
            connection.run(
                f"{get_mender_snapshot_bin(bitbake_variables)} dump "
                + f"--source {passive} | "
                + f"( dd of=/data/snapshot-test bs={len(test_str)} count=1; cat > /dev/null )"
            )

            output = connection.run("cat /data/snapshot-test").stdout.strip()

            assert output == test_str

        finally:
            connection.run("rm -f /data/snapshot-test")

    def test_snapshot_avoid_deadlock(self, bitbake_variables, connection):
        loop = None
        try:
            # We need to create a temporary writable filesystem, because the
            # rootfs filesystem is by default tested with a read-only rootfs,
            # and we need to write a file to the filesystem we dump.
            connection.run(
                f"dd if=/dev/zero of=/data/tmp-file-system count={50 * 2048}",
                # 50 * 2048 * 512 = 50 MiB
            )
            connection.run("mkfs.ext4 /data/tmp-file-system")
            loop = connection.run(
                "losetup --show -f /data/tmp-file-system"
            ).stdout.strip()
            connection.run("mkdir /data/mnt")
            connection.run(f"mount {loop} /data/mnt -t ext4")
            # Fill with some garbage so that we get a bad compression rate and
            # enough data to trigger buffering.
            connection.run(
                f"dd if=/dev/urandom of=/data/mnt/random-data count={10 * 2048}"
            )

            # Try to snapshot to same partition we are freezing.
            result = connection.run(
                f"{get_mender_snapshot_bin(bitbake_variables)} dump "
                + f"--source /data/mnt > /data/mnt/snapshot-test",
                warn=True,
            )
            assert result.return_code != 0
            assert "Freeze timer expired" in result.stderr

            # Do it again, but this time indirectly.
            result = connection.run(
                f"bash -c 'set -o pipefail; {get_mender_snapshot_bin(bitbake_variables)} dump "
                + f"--source /data/mnt | gzip -c > /data/mnt/snapshot-test'",
                warn=True,
            )
            assert result.return_code != 0
            assert "Freeze timer expired" in result.stderr

        finally:
            connection.run("umount /data/mnt || true")
            connection.run("rmdir /data/mnt || true")
            if loop is not None:
                connection.run(f"losetup -d {loop}")
            connection.run("rm -f /data/tmp-file-system")


@pytest.mark.cross_platform
@pytest.mark.only_with_image("uefiimg", "sdimg", "biosimg", "gptimg")
@pytest.mark.usefixtures("setup_board", "bitbake_path")
@pytest.mark.min_mender_version("2.5.0")
# Make sure we run both with and without terminal. Many signal bugs lurk in
# different corners of the console code.
@pytest.mark.parametrize("terminal", ["", "screen -D -m -L -Logfile %%"])
class TestSnapshotMenderArtifact:
    def test_snapshot_using_mender_artifact(
        self, terminal, bitbake_path, bitbake_variables, connection
    ):
        with tempfile.NamedTemporaryFile(
            suffix=".mender"
        ) as artifact, tempfile.NamedTemporaryFile() as screen_log:
            terminal = terminal.replace("%%", screen_log.name)
            (active, _) = determine_active_passive_part(bitbake_variables, connection)

            try:
                subprocess.check_call(
                    f"{terminal} mender-artifact write rootfs-image "
                    + f"{get_ssh_args_mender_artifact(connection)} -n test -t test "
                    + f"-o {artifact.name} "
                    + f"-f ssh://{connection.user}@{connection.host}:{connection.port}",
                    shell=True,
                )
            finally:
                subprocess.call(f"cat {screen_log.name}", shell=True)

            output = subprocess.check_output(
                f"mender-artifact read {artifact.name}", shell=True,
            ).decode()

            partsize = connection.run(f"blockdev --getsize64 {active}").stdout.strip()

            # Ensure that the payload size of the produced artifact matches the
            # partition.
            assert re.search(fr"size: *{partsize}", output) is not None

    def test_snapshot_using_mender_artifact_no_sudo(  # see MEN-3987
        self, terminal, bitbake_path, bitbake_variables, connection
    ):
        with tempfile.NamedTemporaryFile(
            suffix=".mender"
        ) as artifact, tempfile.NamedTemporaryFile() as screen_log:
            terminal = terminal.replace("%%", screen_log.name)
            (active, _) = determine_active_passive_part(bitbake_variables, connection)

            # /usr/bin/sudo is a link to /data/usr/bin/sudo see
            #  meta-mender-qemu/recipes-extended/sudo/sudo_%.bbappend
            sudo_path = "/data/usr/bin/sudo"
            # let's move the sudo away
            result = connection.run(
                f"mv {sudo_path} {sudo_path}-off", warn=True, echo=True
            )
            assert result.return_code == 0

            # lets be sure it does not work
            result = connection.run("sudo --help", echo=True, warn=True)
            assert result.return_code != 0

            try:
                # mender-artifact as of mender-artifact/pull/305 does not use sudo
                #  when user is root or when uid is 0
                subprocess.check_call(
                    f"{terminal} mender-artifact write rootfs-image "
                    + f"{get_ssh_args_mender_artifact(connection)} -n test -t test "
                    + f"-o {artifact.name} "
                    + f"-f ssh://{connection.user}@{connection.host}:{connection.port}",
                    shell=True,
                )
            finally:
                subprocess.call(f"cat {screen_log.name}", shell=True)
                # let's put the sudo back in place and verify that it works
                result = connection.run(
                    f"mv {sudo_path}-off {sudo_path}", warn=True, echo=True
                )
                result = connection.run("sudo --help", echo=True, warn=True)
                assert result.return_code == 0

            output = subprocess.check_output(
                f"mender-artifact read {artifact.name}", shell=True,
            ).decode()

            partsize = connection.run(f"blockdev --getsize64 {active}").stdout.strip()

            # Ensure that the payload size of the produced artifact matches the
            # partition.
            assert re.search(fr"size: *{partsize}", output) is not None
