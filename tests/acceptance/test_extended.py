#!/usr/bin/python
# Copyright 2025 Northern.tech AS
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

import subprocess

import pytest

from utils.common import (
    build_image,
    latest_build_artifact,
)


@pytest.mark.cross_platform
class TestMetaMenderExtended:
    @pytest.mark.only_with_image("ext4")
    def test_build_mender_docker_compose(
        self, request, bitbake_variables, prepared_test_build, bitbake_image
    ):
        build_image(
            prepared_test_build["build_dir"],
            prepared_test_build["bitbake_corebase"],
            bitbake_image,
            [
                'IMAGE_INSTALL:append = " mender-docker-compose"',
                'DISTRO_FEATURES:append = " virtualization"',
                'MENDER_STORAGE_TOTAL_SIZE_MB_DEFAULT = "2048"',
            ],
            [
                f'BBLAYERS:append = " {bitbake_variables["LAYERDIR_MENDER"]}/../meta-mender-extended"',
                f'BBLAYERS:append = " {bitbake_variables["COREBASE"]}/meta-virtualization"',
                f'BBLAYERS:append = " {bitbake_variables["COREBASE"]}/meta-openembedded/meta-networking"',
                f'BBLAYERS:append = " {bitbake_variables["COREBASE"]}/meta-openembedded/meta-filesystems"',
            ],
        )

        image = latest_build_artifact(
            request, prepared_test_build["build_dir"], "core-image*.ext4"
        )

        output = subprocess.check_output(
            ["debugfs", "-R", "stat /usr/share/mender/modules/v3/docker-compose", image]
        ).decode()
        assert "Type: regular" in output

        output = subprocess.check_output(
            ["debugfs", "-R", "stat /etc/mender/mender-docker-compose.conf", image]
        ).decode()
        assert "Type: regular" in output

        output = subprocess.check_output(
            ["debugfs", "-R", "stat /var/lib/mender-docker-compose", image]
        ).decode()
        assert "Type: symlink" in output
        assert 'Fast link dest: "/data/mender-docker-compose"' in output

        data_image = latest_build_artifact(
            request, prepared_test_build["build_dir"], "core-image*.dataimg"
        )

        output = subprocess.check_output(
            ["debugfs", "-R", "stat /mender-docker-compose", data_image]
        ).decode()
        assert "Type: directory" in output
