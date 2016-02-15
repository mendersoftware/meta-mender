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
import unittest

import os.path
import subprocess

# Make sure common is imported after fabric, because we override some functions.
from common import *

@pytest.mark.usefixtures("qemu_running", "no_image_file")
class TestUpdates:
    def test_broken_image_update(self):
        if not env.host_string:
            # This means we are not inside execute(). Recurse into it!
            execute(self.test_broken_image_update)
            return

        # Make a dummy/broken update
        run("dd if=/dev/zero of=image.dat bs=1M count=0 seek=8")
        run("mender -rootfs image.dat")

        try:
            reboot()
            # This should never be reached, because the reconnect should fail.
            assert(False)
        except:
            pass

        kill_qemu()
        start_qemu()

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


    def test_image_update(self):
        if not env.host_string:
            # This means we are not inside execute(). Recurse into it!
            execute(self.test_image_update)
            return

        run("mkfifo image.dat")

        (ssh, host, port) = ssh_prep_args()
        subprocess.Popen(["sh", "-c", "%s %s %s@%s cat \\> image.dat < image.dat" %
                         (ssh, port, env.user, host)])

        run("mender -rootfs image.dat")
        reboot()

        output = run_after_connect("mount")

        # The OS should have moved to /dev/mmcblk0p3, since the image was fine.
        assert(output.find("/dev/mmcblk0p2") < 0)
        assert(output.find("/dev/mmcblk0p3") >= 0)

        output = run("fw_printenv bootcount")
        assert(output == "bootcount=1")

        output = run("fw_printenv upgrade_available")
        assert(output == "upgrade_available=1")

        output = run("fw_printenv boot_part")
        assert(output == "boot_part=3")

        run("mender -commit")

        output = run("fw_printenv bootcount")
        assert(output == "bootcount=0")

        output = run("fw_printenv upgrade_available")
        assert(output == "upgrade_available=0")

        output = run("fw_printenv boot_part")
        assert(output == "boot_part=3")

        reboot()

        output = run_after_connect("mount")

        # The OS should have moved to /dev/mmcblk0p3, since we committed.
        assert(output.find("/dev/mmcblk0p2") < 0)
        assert(output.find("/dev/mmcblk0p3") >= 0)
