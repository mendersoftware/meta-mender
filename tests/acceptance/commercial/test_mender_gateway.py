#!/usr/bin/python
# Copyright 2022 Northern.tech AS
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


@pytest.mark.commercial
@pytest.mark.min_mender_version("3.3.0")
class TestMenderGateway:
    @pytest.mark.only_with_image("ext4")
    def test_build_mender_gateway(
        self, request, bitbake_variables, prepared_test_build, bitbake_image
    ):
        build_image(
            prepared_test_build["build_dir"],
            prepared_test_build["bitbake_corebase"],
            bitbake_image,
            ['IMAGE_INSTALL:append = " mender-gateway"'],
            [
                'BBLAYERS:append = " %s/../meta-mender-commercial"'
                % bitbake_variables["LAYERDIR_MENDER"]
            ],
        )
        image = latest_build_artifact(
            request, prepared_test_build["build_dir"], "core-image*.ext4"
        )

        for file in (
            "/usr/bin/mender-gateway",
            "/usr/share/mender/inventory/mender-inventory-mender-gateway",
        ):
            output = subprocess.check_output(
                ["debugfs", "-R", f"stat {file}", image]
            ).decode()
            assert "Type: regular" in output
