#!/usr/bin/python
# Copyright 2020 Northern.tech AS
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
import os
import subprocess

import pytest

from utils.common import determine_active_passive_part, get_ssh_common_args


@pytest.mark.usefixtures("setup_board", "bitbake_path")
class TestSnapshot:
    @pytest.mark.min_mender_version("2.2.0")
    @pytest.mark.only_with_image("uefiimg", "sdimg", "biosimg", "gptimg")
    @pytest.mark.parametrize("compression", [("", ">"), ("-C gzip", "| gunzip -c >")])
    def test_basic_snapshot(self, compression, bitbake_variables, connection):
        try:
            (active, passive) = determine_active_passive_part(
                bitbake_variables, connection
            )

            # Wipe the inactive partition first.
            connection.run("dd if=/dev/zero of=%s bs=1M count=100" % passive)

            # Dump what we currently have to the inactive partition.
            connection.run(
                "mender snapshot dump %s %s %s"
                % (compression[0], compression[1], passive)
            )

            # Make sure this looks like a sane filesystem.
            connection.run("fsck.ext4 -p %s" % passive)

            # And that it can be mounted with actual content.
            connection.run("mount %s /mnt" % passive)
            connection.run("test -f /mnt/etc/passwd")

        finally:
            connection.run("umount /mnt || true")

    @pytest.mark.min_mender_version("2.2.0")
    @pytest.mark.only_with_image("uefiimg", "sdimg", "biosimg", "gptimg")
    def test_snapshot_device_file(self, bitbake_variables, connection):
        try:
            (active, passive) = determine_active_passive_part(
                bitbake_variables, connection
            )

            # Wipe the inactive partition first.
            connection.run("dd if=/dev/zero of=%s bs=1M count=100" % passive)

            # Dump what we currently have to the inactive partition, using
            # device file reference.
            connection.run("mender snapshot dump --source %s > %s" % (active, passive))

            # Make sure this looks like a sane filesystem.
            connection.run("fsck.ext4 -p %s" % passive)

            # And that it can be mounted with actual content.
            connection.run("mount %s /mnt" % passive)
            connection.run("test -f /mnt/etc/passwd")

        finally:
            connection.run("umount /mnt || true")

    @pytest.mark.min_mender_version("2.2.0")
    @pytest.mark.only_with_image("uefiimg", "sdimg", "biosimg", "gptimg")
    def test_snapshot_inactive(self, bitbake_variables, connection):
        try:
            (active, passive) = determine_active_passive_part(
                bitbake_variables, connection
            )

            test_str = "TeSt StrIng!#"

            # Seed the initial part of the inactive partition with a test string
            connection.run("echo '%s' | dd of=%s" % (test_str, passive))

            # Try to snapshot inactive partition, keeping the initial part, and
            # dumping the rest.
            connection.run(
                "mender snapshot dump --source %s | ( dd of=/data/snapshot-test bs=%d count=1; cat > /dev/null )"
                % (passive, len(test_str))
            )

            output = connection.run("cat /data/snapshot-test").stdout.strip()

            assert output == test_str

        finally:
            connection.run("rm -f /data/snapshot-test")

    @pytest.mark.min_mender_version("2.2.0")
    @pytest.mark.only_with_image("uefiimg", "sdimg", "biosimg", "gptimg")
    def test_snapshot_avoid_deadlock(self, connection):
        loop = None
        try:
            # We need to create a temporary writable filesystem, because the
            # rootfs filesystem is by default tested with a read-only rootfs,
            # and we need to write a file to the filesystem we dump.
            connection.run(
                "dd if=/dev/zero of=/data/tmp-file-system count=%d"
                % (50 * 2048)  # 50 * 2048 * 512 = 50 MiB
            )
            connection.run("mkfs.ext4 /data/tmp-file-system")
            loop = connection.run(
                "losetup --show -f /data/tmp-file-system"
            ).stdout.strip()
            connection.run("mkdir /data/mnt")
            connection.run("mount %s /data/mnt -t ext4" % loop)
            # Fill with some garbage so that we get a bad compression rate and
            # enough data to trigger buffering.
            connection.run(
                "dd if=/dev/urandom of=/data/mnt/random-data count=%d" % (10 * 2048)
            )

            # Try to snapshot to same partition we are freezing.
            result = connection.run(
                "mender snapshot dump --source /data/mnt > /data/mnt/snapshot-test",
                warn=True,
            )
            assert result.return_code != 0
            assert "Freeze timer expired" in result.stderr

            # Do it again, but this time indirectly.
            result = connection.run(
                "bash -c 'set -o pipefail; mender snapshot dump --source /data/mnt | gzip -c > /data/mnt/snapshot-test'",
                warn=True,
            )
            assert result.return_code != 0
            assert "Freeze timer expired" in result.stderr

        finally:
            connection.run("umount /data/mnt || true")
            connection.run("rmdir /data/mnt || true")
            if loop is not None:
                connection.run("losetup -d %s" % loop)
            connection.run("rm -f /data/tmp-file-system")

    @pytest.mark.min_mender_version("2.2.0")
    @pytest.mark.only_with_image("uefiimg", "sdimg", "biosimg", "gptimg")
    # Make sure we run both with and without terminal. Many signal bugs lurk in
    # different corners of the console code.
    @pytest.mark.parametrize(
        "terminal", ["", "screen -D -m -L -Logfile screen.log.tmp"]
    )
    def test_snapshot_using_mender_artifact(
        self, terminal, bitbake_path, bitbake_variables, connection
    ):
        try:
            (active, passive) = determine_active_passive_part(
                bitbake_variables, connection
            )

            common_args = get_ssh_common_args(connection)
            # mender-artifact prefixes each ssh argument with "-S"
            common_args = common_args.replace(" ", " -S ")

            try:
                subprocess.check_call(
                    "%s mender-artifact write rootfs-image -S %s -n test -t test -o test_snapshot_using_mender_artifact.mender -f ssh://%s@%s:%s"
                    % (
                        terminal,
                        common_args,
                        connection.user,
                        connection.host,
                        connection.port,
                    ),
                    shell=True,
                )
            finally:
                subprocess.call("cat screen.log.tmp ; rm -f screen.log.tmp", shell=True)

            output = subprocess.check_output(
                "mender-artifact read test_snapshot_using_mender_artifact.mender",
                shell=True,
            ).decode()

            partsize = connection.run("blockdev --getsize64 %s" % active).stdout.strip()

            # Ensure that the payload size of the produced artifact matches the
            # partition.
            assert re.search("size: *%s" % partsize, output) is not None

        finally:
            try:
                os.remove("test_snapshot_using_mender_artifact.mender")
            except:
                pass
