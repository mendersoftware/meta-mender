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

@pytest.mark.commercial
@pytest.mark.min_mender_version("2.1.0")
class TestDeltaUpdateModule:

    @pytest.mark.only_with_image('ext4')
    def test_build_and_run_module(self, bitbake_variables, prepared_test_build):
        add_to_local_conf(prepared_test_build, 'IMAGE_INSTALL_append = " mender-binary-delta"')
        add_to_bblayers_conf(prepared_test_build, 'BBLAYERS_append = " %s/../meta-mender-commercial"'
                             % bitbake_variables['LAYERDIR_MENDER'])

        run_bitbake(prepared_test_build)

        image = latest_build_artifact(prepared_test_build['build_dir'], "core-image*.ext4")
        output = subprocess.check_output(["debugfs", "-R", "ls -p /usr/share/mender/modules/v3", image])

        # Debugfs has output like this:
        #   /3018/100755/0/0/mender-binary-delta/142672/
        #   /3015/100755/0/0/rootfs-image-v2/1606/
        assert "mender-binary-delta" in [line.split('/')[5] for line in output.split('\n') if line.startswith('/')]
