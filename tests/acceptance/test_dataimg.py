#!/usr/bin/python
# Copyright 2017 Northern.tech AS
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

import os
import subprocess

import pytest

from utils.common import build_image, latest_build_artifact, make_tempdir


class TestDataImg:
    @pytest.mark.min_mender_version("1.0.0")
    def test_dataimg_creation(
        self, request, bitbake_variables, prepared_test_build, bitbake_image
    ):
        """Test that we can build a dataimg successfully."""

        build_image(
            prepared_test_build["build_dir"],
            prepared_test_build["bitbake_corebase"],
            bitbake_image,
            ['IMAGE_FSTYPES = "dataimg"'],
        )

        built_img = latest_build_artifact(
            request, prepared_test_build["build_dir"], "core-image*.dataimg"
        )

        # Check that it contains the device_type file, as we expect.
        with make_tempdir() as tmpdir:
            menderdir = os.path.join(tmpdir, "mender")
            if (
                "ARTIFACTIMG_FSTYPE" in bitbake_variables
                and bitbake_variables["ARTIFACTIMG_FSTYPE"] == "ubifs"
            ):
                subprocess.check_call(
                    ["ubireader_extract_files", "-o", tmpdir, built_img]
                )
            else:
                os.mkdir(menderdir)
                subprocess.check_call(
                    [
                        "debugfs",
                        "-R",
                        "dump -p /mender/device_type %s"
                        % os.path.join(menderdir, "device_type"),
                        built_img,
                    ]
                )
            with open(os.path.join(menderdir, "device_type")) as fd:
                content = fd.read()
            assert (
                content == "device_type=%s\n" % bitbake_variables["MENDER_DEVICE_TYPE"]
            )
