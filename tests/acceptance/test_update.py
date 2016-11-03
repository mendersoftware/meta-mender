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

if pytest.config.getoption("--bbb"):
    image_type = "beaglebone"
else:
    image_type = "vexpress-qemu"

class Helpers:
    @staticmethod
    def upload_to_s3():
        subprocess.call(["s3cmd", "--follow-symlinks", "put", "successful_image_update.dat", "s3://mender/temp/"])
        subprocess.call(["s3cmd", "setacl", "s3://mender/temp/successful_image_update.dat", "--acl-public"])

    @staticmethod
    # TODO: Use this when mender is more stable. Spurious errors are currently generated.
    def check_journal_errors():
        output = run("journalctl -a -u mender | grep error")
        assert output == 1

@pytest.mark.usefixtures("qemu_running", "no_image_file", "setup_bbb", "bitbake_path")
class TestUpdates:

    def test_broken_image_update(self):

        if not env.host_string:
            # This means we are not inside execute(). Recurse into it!
            execute(self.test_broken_image_update)
            return

        # Make a dummy/broken update
        subprocess.call("dd if=/dev/zero of=image.dat bs=1M count=0 seek=8", shell=True)
        subprocess.call("artifacts write rootfs-image -t %s -i test-update -u image.dat -o image.mender" % image_type, shell=True)
        put("image.mender", remote_path="/var/tmp/image.mender")
        run("mender -rootfs /var/tmp/image.mender")
        reboot()

        # Now qemu is auto-rebooted twice; once to boot the dummy image,
        # where it fails, and uboot auto-reboots a second time into the
        # original partition.

        output = run_after_connect("mount")

        # The update should have reverted to /dev/mmcblk0p2, since the image was
        # bogus.
        assert(output.find("/dev/mmcblk0p2") >= 0)
        assert(output.find("/dev/mmcblk0p3") < 0)

        # Cleanup.
        os.remove("image.mender")
        os.remove("image.dat")

    def test_too_big_image_update(self):
        if not env.host_string:
            # This means we are not inside execute(). Recurse into it!
            execute(self.test_too_big_image_update)
            return

        # Make a too big update
        subprocess.call("dd if=/dev/zero of=image.dat bs=1M count=0 seek=1024", shell=True)
        subprocess.call("artifacts write rootfs-image -t %s -i test-update-too-big -u image.dat -o image-too-big.mender" % image_type, shell=True)
        put("image-too-big.mender", remote_path="/var/tmp/image-too-big.mender")
        output = run("mender -rootfs /var/tmp/image-too-big.mender ; echo 'ret_code=$?'")

        assert(output.find("no space left on device") >= 0)
        assert(output.find("ret_code=0") < 0)

        # Cleanup.
        os.remove("image-too-big.mender")
        os.remove("image.dat")

    def test_network_based_image_update(self):
        http_server_location = pytest.config.getoption("--http-server")
        bbb = pytest.config.getoption("--bbb")

        if not env.host_string:
            # This means we are not inside execute(). Recurse into it!
            execute(self.test_network_based_image_update)
            return

        output = run("mount")
        (active_before, passive_before) = determine_active_passive_part(output)

        if bbb:
            Helpers.upload_to_s3()
            http_server_location = "s3.amazonaws.com/mender/temp"
        else:
            http_server = subprocess.Popen(["python", "-m", "SimpleHTTPServer"])
            assert(http_server)

        try:
            run("mender -rootfs http://%s/successful_image_update.dat" % (http_server_location))
        finally:
            if not bbb:
                http_server.terminate()

        output = run("fw_printenv bootcount")
        assert(output == "bootcount=0")

        output = run("fw_printenv upgrade_available")
        assert(output == "upgrade_available=1")

        output = run("fw_printenv mender_boot_part")
        assert(output == "mender_boot_part=" + passive_before)

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

        output = run("fw_printenv mender_boot_part")
        assert(output == "mender_boot_part=" + active_after)

        run("mender -commit")

        output = run("fw_printenv upgrade_available")
        assert(output == "upgrade_available=0")

        output = run("fw_printenv mender_boot_part")
        assert(output == "mender_boot_part=" + active_after)

        active_before = active_after
        passive_before = passive_after

        reboot()

        output = run_after_connect("mount")
        (active_after, passive_after) = determine_active_passive_part(output)

        # The OS should have stayed on the same partition, since we committed.
        assert(active_after == active_before)
        assert(passive_after == passive_before)
