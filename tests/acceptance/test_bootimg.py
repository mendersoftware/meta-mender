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

import os
import pytest
import subprocess

# Make sure common is imported after fabric, because we override some functions.
from common import *

class TestBootImg:
    @pytest.mark.min_mender_version('1.0.0')
    def test_bootimg_creation(self, bitbake_variables, prepared_test_build):
        """Test that we can build a bootimg successfully."""

        add_to_local_conf(prepared_test_build, 'IMAGE_FSTYPES = "bootimg"')
        run_bitbake(prepared_test_build)

        built_img = latest_build_artifact(prepared_test_build['build_dir'], "core-image*.bootimg")

        # What can we check here to validate this?
