#!/usr/bin/python
# Copyright 2019 Northern.tech AS
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

import distutils.spawn
import os
import re
import shutil
import subprocess

import pytest

from utils.common import (
    build_image,
    latest_build_artifact,
    reboot,
    run_after_connect,
    determine_active_passive_part,
    make_tempdir,
)
from utils.helpers import Helpers


@pytest.mark.commercial
@pytest.mark.min_mender_version("2.1.0")
class TestDeltaUpdateModule:
    @pytest.mark.only_with_image("ext4")
    def test_build_and_run_module(
        self, request, bitbake_variables, prepared_test_build, bitbake_image
    ):

        build_image(
            prepared_test_build["build_dir"],
            prepared_test_build["bitbake_corebase"],
            bitbake_image,
            ['IMAGE_INSTALL_append = " mender-binary-delta"'],
            [
                'BBLAYERS_append = " %s/../meta-mender-commercial"'
                % bitbake_variables["LAYERDIR_MENDER"]
            ],
        )

        image = latest_build_artifact(
            request, prepared_test_build["build_dir"], "core-image*.ext4"
        )
        output = subprocess.check_output(
            ["debugfs", "-R", "ls -p /usr/share/mender/modules/v3", image]
        ).decode()

        # Debugfs has output like this:
        #   /3018/100755/0/0/mender-binary-delta/142672/
        #   /3015/100755/0/0/rootfs-image-v2/1606/
        assert "mender-binary-delta" in [
            line.split("/")[5] for line in output.split("\n") if line.startswith("/")
        ]

    def do_install_mender_binary_delta(
        self,
        request,
        prepared_test_build,
        bitbake_variables,
        bitbake_image,
        connection,
        http_server,
        board_type,
        use_s3,
        s3_address,
    ):
        build_image(
            prepared_test_build["build_dir"],
            prepared_test_build["bitbake_corebase"],
            bitbake_image,
            ['IMAGE_INSTALL_append = " mender-binary-delta"'],
            [
                'BBLAYERS_append = " %s/../meta-mender-commercial"'
                % bitbake_variables["LAYERDIR_MENDER"]
            ],
        )

        image = latest_build_artifact(
            request, prepared_test_build["build_dir"], "core-image*.mender"
        )

        Helpers.install_update(
            image, connection, http_server, board_type, use_s3, s3_address
        )

        reboot(connection)

        run_after_connect("true", connection)
        connection.run("mender -commit")

        return image

    @pytest.mark.only_with_image("ext4")
    def test_runtime_checksum(
        self,
        request,
        setup_board,
        prepared_test_build,
        bitbake_variables,
        bitbake_image,
        connection,
        http_server,
        board_type,
        use_s3,
        s3_address,
    ):
        """Check that the checksum of the running root filesystem is what we
        expect. This is important in order for it to match when applying a delta
        update.

        """

        if (
            "read-only-rootfs"
            not in bitbake_variables["IMAGE_FEATURES"].strip().split()
        ):
            pytest.skip("Only works when using read-only-rootfs IMAGE_FEATURE")

        image = self.do_install_mender_binary_delta(
            request,
            prepared_test_build,
            bitbake_variables,
            bitbake_image,
            connection,
            http_server,
            board_type,
            use_s3,
            s3_address,
        )

        # Check that checksum of the currently mounted rootfs matches that
        # of the artifact which we just updated to.
        (active, _) = determine_active_passive_part(bitbake_variables, connection)
        output = connection.run("sha256sum %s" % active)
        rootfs_sum = output.stdout.split()[0]
        output = subprocess.check_output(
            "mender-artifact read %s" % image, shell=True
        ).decode()
        match = re.search("checksum: *([0-9a-f]+)", output)
        assert match is not None, (
            "Could not find checksum in mender-artifact output: %s" % output
        )
        artifact_sum = match.group(1)
        assert rootfs_sum == artifact_sum

    # Not testable on QEMU/ARM combination currently. See MEN-4297.
    @pytest.mark.not_for_machine("vexpress-qemu")
    # mender-binary-delta 1.2.0 requires mender-artifact 3.5.0
    @pytest.mark.min_mender_version("2.5.0")
    @pytest.mark.only_with_image("ext4")
    def test_perform_update(
        self,
        request,
        setup_board,
        prepared_test_build,
        bitbake_variables,
        bitbake_image,
        connection,
        http_server,
        board_type,
        use_s3,
        s3_address,
    ):
        """Perform a delta update.

        """

        if (
            "read-only-rootfs"
            not in bitbake_variables["IMAGE_FEATURES"].strip().split()
        ):
            pytest.skip("Only works when using read-only-rootfs IMAGE_FEATURE")

        if distutils.spawn.find_executable("mender-binary-delta-generator") is None:
            pytest.fail("mender-binary-delta-generator not found in PATH")

        built_artifact = self.do_install_mender_binary_delta(
            request,
            prepared_test_build,
            bitbake_variables,
            bitbake_image,
            connection,
            http_server,
            board_type,
            use_s3,
            s3_address,
        )

        with make_tempdir() as tmpdir:
            # Copy previous build
            artifact_from = os.path.join(tmpdir, "artifact_from.mender")
            shutil.copyfile(built_artifact, artifact_from)

            # Create new image installing some extra software
            build_image(
                prepared_test_build["build_dir"],
                prepared_test_build["bitbake_corebase"],
                bitbake_image,
                ['IMAGE_INSTALL_append = " nano"'],
            )
            built_artifact = latest_build_artifact(
                request, prepared_test_build["build_dir"], "core-image*.mender"
            )
            artifact_to = os.path.join(tmpdir, "artifact_to.mender")
            shutil.copyfile(built_artifact, artifact_to)

            # Create delta Artifact using mender-binary-delta-generator
            artifact_delta = os.path.join(tmpdir, "artifact_delta.mender")
            subprocess.check_call(
                f"mender-binary-delta-generator -n v2.0-deltafrom-v1.0 {artifact_from} {artifact_to} -o {artifact_delta}",
                shell=True,
            )

            # Verbose provides/depends of the different Artifacts and the client (when supported)
            connection.run("mender show-provides", warn=True)
            subprocess.check_call(
                "mender-artifact read %s" % artifact_from, shell=True,
            )
            subprocess.check_call(
                "mender-artifact read %s" % artifact_to, shell=True,
            )
            subprocess.check_call(
                "mender-artifact read %s" % artifact_delta, shell=True,
            )

            # Install Artifact, verify partitions and commit
            (active, passive) = determine_active_passive_part(
                bitbake_variables, connection
            )
            Helpers.install_update(
                artifact_delta, connection, http_server, board_type, use_s3, s3_address
            )
            reboot(connection)
            run_after_connect("true", connection)
            (new_active, new_passive) = determine_active_passive_part(
                bitbake_variables, connection
            )
            assert new_active == passive
            assert new_passive == active
            connection.run("mender -commit")
