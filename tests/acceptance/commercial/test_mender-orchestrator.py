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
import os

import pytest

from utils.common import (
    build_image,
    latest_build_artifact,
)


@pytest.mark.cross_platform
@pytest.mark.commercial
@pytest.mark.min_mender_version("4.0.0")
class TestMenderOrchestrator:
    @pytest.mark.only_with_image("ext4")
    def test_build_mender_orchestrator(
        self, request, bitbake_variables, prepared_test_build, bitbake_image
    ):
        # Get the directory where this test file is located
        test_dir = os.path.dirname(os.path.abspath(__file__))

        build_image(
            prepared_test_build["build_dir"],
            prepared_test_build["bitbake_corebase"],
            bitbake_image,
            ['IMAGE_INSTALL:append = " mender-orchestrator"'],
            [
                'BBLAYERS:append = " %s/../meta-mender-commercial"'
                % bitbake_variables["LAYERDIR_MENDER"],
                f'FILESEXTRAPATHS:prepend:pn-mender-orchestrator = "{test_dir}/files:"',
                'SRC_URI:append:pn-mender-orchestrator = " file://topology.yaml"',
            ],
        )

        image = latest_build_artifact(
            request, prepared_test_build["build_dir"], "core-image*.ext4"
        )

        for file in (
            "/usr/bin/mender-orchestrator",
            "/data/mender-orchestrator/manifests/topology.yaml",
            "/usr/share/mender/inventory/mender-inventory-orchestrator-inventory",
        ):
            output = subprocess.check_output(
                ["debugfs", "-R", f"stat {file}", image]
            ).decode()
            assert "Type: regular" in output

        output = subprocess.check_output(
            ["debugfs", "-R", "stat /var/lib/mender-orchestrator", image]
        ).decode()
        assert "Type: symlink" in output
        assert 'Fast link dest: "/data/mender-orchestrator"' in output
