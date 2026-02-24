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
    make_tempdir,
)


def check_common_orchestrator_files(
    request, prepared_test_build, bitbake_variables, test_dir
):
    ext4_image = latest_build_artifact(
        request, prepared_test_build["build_dir"], "core-image*.ext4"
    )
    output = subprocess.check_output(
        ["debugfs", "-R", "stat /usr/bin/mender-orchestrator", ext4_image]
    ).decode()
    assert "Type: regular" in output

    output = subprocess.check_output(
        ["debugfs", "-R", "stat /var/lib/mender-orchestrator", ext4_image]
    ).decode()
    assert "Type: symlink" in output
    assert 'Fast link dest: "/data/mender-orchestrator"' in output

    image = latest_build_artifact(
        request, prepared_test_build["build_dir"], "core-image*.dataimg"
    )
    with make_tempdir() as tmpdir:
        mender_orch_dir = os.path.join(tmpdir, "mender-orchestrator")
        if (
            "ARTIFACTIMG_FSTYPE" in bitbake_variables
            and bitbake_variables["ARTIFACTIMG_FSTYPE"] == "ubifs"
        ):
            subprocess.check_call(["ubireader_extract_files", "-o", tmpdir, image])
        else:
            os.mkdir(mender_orch_dir)
            subprocess.check_call(
                [
                    "debugfs",
                    "-R",
                    f"dump -p /mender-orchestrator/topology.yaml {os.path.join(mender_orch_dir, 'topology.yaml')}",
                    image,
                ]
            )
        with open(os.path.join(mender_orch_dir, "topology.yaml")) as fd_data:
            data_topology = fd_data.read()
            with open(os.path.join(test_dir, "files", "topology.yaml")) as fd:
                test_topology = fd.read()
                assert (
                    data_topology == test_topology
                ), "Error: the installed topology doesn't match"


@pytest.mark.cross_platform
@pytest.mark.commercial
@pytest.mark.min_mender_version("4.0.0")
@pytest.mark.only_with_image("ext4")
class TestMenderOrchestrator:
    def test_build_mender_orchestrator(
        self, request, bitbake_variables, prepared_test_build, bitbake_image
    ):
        test_dir = os.path.dirname(os.path.abspath(__file__))

        build_image(
            prepared_test_build["build_dir"],
            prepared_test_build["bitbake_corebase"],
            bitbake_image,
            [
                'IMAGE_INSTALL:append = " mender-orchestrator"',
                f'FILESEXTRAPATHS:prepend := "{test_dir}/files:"',
                'SRC_URI:append:pn-mender-orchestrator = " file://topology.yaml"',
            ],
            [
                'BBLAYERS:append = " %s/../meta-mender-commercial"'
                % bitbake_variables["LAYERDIR_MENDER"],
            ],
        )

        check_common_orchestrator_files(
            request, prepared_test_build, bitbake_variables, test_dir
        )
