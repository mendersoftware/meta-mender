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

import subprocess

import pytest

from utils.common import build_image, latest_build_artifact


class TestBootImg:
    @pytest.mark.min_mender_version("1.0.0")
    def test_bootimg_creation(
        self, request, bitbake_variables, prepared_test_build, bitbake_image
    ):
        """Test that we can build a bootimg successfully."""

        build_image(
            prepared_test_build["build_dir"],
            prepared_test_build["bitbake_corebase"],
            bitbake_image,
            ['IMAGE_FSTYPES = "bootimg"'],
        )

        built_img = latest_build_artifact(
            request, prepared_test_build["build_dir"], "core-image*.bootimg"
        )

        distro_features = bitbake_variables["DISTRO_FEATURES"].split()
        if "mender-grub" in distro_features and "mender-image-uefi" in distro_features:
            output = subprocess.check_output(
                ["mdir", "-i", built_img, "-b", "/EFI/BOOT"]
            ).decode()
            assert "mender_grubenv1" in output.split("/")
