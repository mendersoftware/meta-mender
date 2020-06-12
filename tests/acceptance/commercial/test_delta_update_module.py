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

import pytest
import subprocess

from common import *
from helpers import Helpers


@pytest.mark.commercial
@pytest.mark.min_mender_version("2.1.0")
class TestDeltaUpdateModule:
    @pytest.mark.only_with_image("ext4")
    def test_build_and_run_module(
        self, bitbake_variables, prepared_test_build, bitbake_image
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
            prepared_test_build["build_dir"], "core-image*.ext4"
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

    @pytest.mark.only_with_image("ext4")
    def test_runtime_checksum(
        self,
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
            prepared_test_build["build_dir"], "core-image*.mender"
        )

        Helpers.install_update(
            image, connection, http_server, board_type, use_s3, s3_address,
        )

        reboot(connection)

        run_after_connect("true", connection)
        (active, _) = determine_active_passive_part(bitbake_variables, connection)

        connection.run("mender -commit")

        # Check that checksum of the currently mounted rootfs matches that
        # of the artifact which we just updated to.
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
