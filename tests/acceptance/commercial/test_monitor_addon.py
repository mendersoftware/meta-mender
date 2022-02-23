#!/usr/bin/python
# Copyright 2021 Northern.tech AS
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
@pytest.mark.min_mender_version("3.1.0")
class TestMonitorAddon:
    @pytest.mark.only_with_image("ext4")
    def test_build_addon(
        self, request, bitbake_variables, prepared_test_build, bitbake_image
    ):
        build_image(
            prepared_test_build["build_dir"],
            prepared_test_build["bitbake_corebase"],
            bitbake_image,
            ['IMAGE_INSTALL:append = " mender-monitor"'],
            [
                'BBLAYERS:append = " %s/../meta-mender-commercial"'
                % bitbake_variables["LAYERDIR_MENDER"]
            ],
        )
        image = latest_build_artifact(
            request, prepared_test_build["build_dir"], "core-image*.ext4"
        )

        for expected_node in [
            "/usr/bin/mender-monitorctl",
            "/usr/bin/mender-monitord",
            "/etc/mender-monitor/monitor.d/log.sh",
            "/etc/mender-monitor/monitor.d/service.sh",
            "/usr/share/mender-monitor/mender-monitorctl",
            "/usr/share/mender-monitor/mender-monitord",
            "/usr/share/mender-monitor/ctl.sh",
            "/usr/share/mender-monitor/daemon.sh",
            "/usr/share/mender-monitor/common/common.sh",
            "/usr/share/mender-monitor/config/config.sh",
            "/usr/share/mender-monitor/lib/monitor-lib.sh",
            "/usr/share/mender-monitor/lib/service-lib.sh",
            "/var/lib/mender-monitor",
        ]:
            output = subprocess.check_output(
                ["debugfs", "-R", "stat %s" % expected_node, image]
            ).decode()

            # The nodes are either files or symlinks
            assert "Type: regular" in output or "Type: symlink" in output
