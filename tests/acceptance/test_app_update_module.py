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

import subprocess

import pytest

from utils.common import (
    build_image,
    latest_build_artifact,
)


class TestAppUpdateModule:
    @pytest.mark.min_mender_version("1.0.0")
    @pytest.mark.only_with_image("ext4")
    def test_build_app_update_module(self, request, prepared_test_build, bitbake_image):
        build_image(
            prepared_test_build["build_dir"],
            prepared_test_build["bitbake_corebase"],
            bitbake_image,
            ['IMAGE_INSTALL:append = " mender-app-update-module"'],
        )
        image = latest_build_artifact(
            request, prepared_test_build["build_dir"], "core-image*.ext4"
        )

        for expected_node in ("/usr/share/mender/modules/v3/app",):
            output = subprocess.check_output(
                ["debugfs", "-R", "stat %s" % expected_node, image]
            ).decode()

            # The nodes are either files or symlinks
            assert "Type: regular" in output or "Type: symlink" in output
