#!/usr/bin/python
# Copyright 2016 Mender Software AS
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

from fabric.api import *

import pytest
import subprocess

# Make sure common is imported after fabric, because we override some functions.
from common import *


@pytest.mark.usefixtures("qemu_running", "no_image_file", "setup_bbb")
class TestUpdates:

    @pytest.mark.skip(pytest.config.getoption("--bbb"), reason="broken on bbb.")
    def test_broken_image_update(self):
        if not env.host_string:
            # This means we are not inside execute(). Recurse into it!
            execute(self.test_broken_image_update)
            return

        # Make a dummy/broken update
        run("dd if=/dev/zero of=image.dat bs=1M count=0 seek=8")
        run("mender -rootfs image.dat")
        reboot()

        # Now qemu is auto-rebooted twice; once to boot the dummy image,
        # where it fails, and uboot auto-reboots a second time into the
        # original parition.

        output = run_after_connect("mount")

        # The update should have reverted to /dev/mmcblk0p2, since the image was
        # bogus.
        assert(output.find("/dev/mmcblk0p2") >= 0)
        assert(output.find("/dev/mmcblk0p3") < 0)

    def test_too_big_image_update(self):
        if not env.host_string:
            # This means we are not inside execute(). Recurse into it!
            execute(self.test_too_big_image_update)
            return

        # Make a too big update
        run("dd if=/dev/zero of=image.dat bs=1M count=0 seek=2048")
        output = run('mender -rootfs image.dat ; echo "ret_code=$?"')

        assert(output.find("smaller") >= 0)
        assert(output.find("ret_code=0") < 0)

    def test_file_based_image_update(self):
        if not env.host_string:
            # This means we are not inside execute(). Recurse into it!
            execute(self.test_file_based_image_update)
            return

        output = run("mount")
        (active_before, passive_before) = determine_active_passive_part(output)

        run("mkfifo image.dat")

        # Horrible hack to emulate a file which is as big as we need.
        (ssh, host, port) = ssh_prep_args()
        subprocess.Popen(["sh", "-c", "%s %s %s@%s cat \\> image.dat < image.dat" %
                         (ssh, port, env.user, host)])

        run("mender -rootfs image.dat")

        output = run("fw_printenv bootcount")
        assert(output == "bootcount=0")

        output = run("fw_printenv upgrade_available")
        assert(output == "upgrade_available=1")

        output = run("fw_printenv boot_part")
        assert(output == "boot_part=" + passive_before)

        reboot()

        output = run_after_connect("mount")
        (active_after, passive_after) = determine_active_passive_part(output)

        # The OS should have moved to a new partition, since the image was fine.
        assert(active_after == passive_before)
        assert(passive_after == active_before)

        output = run("fw_printenv bootcount")
        assert(output == "bootcount=1")

        output = run("fw_printenv upgrade_available")
        assert(output == "upgrade_available=1")

        output = run("fw_printenv boot_part")
        assert(output == "boot_part=" + active_after)

        run("mender -commit")

        output = run("fw_printenv upgrade_available")
        assert(output == "upgrade_available=0")

        output = run("fw_printenv boot_part")
        assert(output == "boot_part=" + active_after)

        active_before = active_after
        passive_before = passive_after

        reboot()

        output = run_after_connect("mount")
        (active_after, passive_after) = determine_active_passive_part(output)

        # The OS should have stayed on the same partition, since we committed.
        assert(active_after == active_before)
        assert(passive_after == passive_before)

    def test_network_based_image_update(self):
        http_server_location = pytest.config.getoption("--http-server")
        if not env.host_string:
            # This means we are not inside execute(). Recurse into it!
            execute(self.test_network_based_image_update)
            return

        output = run("mount")
        (active_before, passive_before) = determine_active_passive_part(output)

        http_server = subprocess.Popen(["python", "-m", "SimpleHTTPServer"])
        assert(http_server)

        try:
            sudo("mender -rootfs http://%s/image.dat" % (http_server_location))
        finally:
            http_server.terminate()

        output = run("fw_printenv bootcount")
        assert(output == "bootcount=0")

        output = run("fw_printenv upgrade_available")
        assert(output == "upgrade_available=1")

        output = run("fw_printenv boot_part")
        assert(output == "boot_part=" + passive_before)

        reboot()

        output = run_after_connect("mount")
        (active_after, passive_after) = determine_active_passive_part(output)

        # The OS should have moved to a new partition, since the image was fine.
        assert(active_after == passive_before)
        assert(passive_after == active_before)

        output = run("fw_printenv bootcount")
        assert(output == "bootcount=1")

        output = run("fw_printenv upgrade_available")
        assert(output == "upgrade_available=1")

        output = run("fw_printenv boot_part")
        assert(output == "boot_part=" + active_after)

        run("mender -commit")

        output = run("fw_printenv upgrade_available")
        assert(output == "upgrade_available=0")

        output = run("fw_printenv boot_part")
        assert(output == "boot_part=" + active_after)

        active_before = active_after
        passive_before = passive_after

        reboot()

        output = run_after_connect("mount")
        (active_after, passive_after) = determine_active_passive_part(output)

        # The OS should have stayed on the same partition, since we committed.
        assert(active_after == active_before)
        assert(passive_after == passive_before)
