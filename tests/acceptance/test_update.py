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
        subprocess.call(["s3cmd", "--follow-symlinks", "put", "successful_image_update.mender", "s3://mender/temp/"])
        subprocess.call(["s3cmd", "setacl", "s3://mender/temp/successful_image_update.mender", "--acl-public"])

    @staticmethod
    # TODO: Use this when mender is more stable. Spurious errors are currently generated.
    def check_journal_errors():
        output = run("journalctl -a -u mender | grep error")
        assert output == 1

    @staticmethod
    def get_env_offsets(bitbake_variables):
        offsets = [0, 0]

        alignment = int(bitbake_variables["MENDER_PARTITION_ALIGNMENT_KB"]) * 1024
        env_size = os.stat(os.path.join(bitbake_variables["DEPLOY_DIR_IMAGE"], "uboot.env")).st_size
        offsets[0] = int(bitbake_variables["MENDER_UBOOT_ENV_STORAGE_DEVICE_OFFSET"])
        offsets[1] = offsets[0] + int(env_size / 2)

        assert(offsets[0] % alignment == 0)
        assert(offsets[1] % alignment == 0)

        return offsets

    @staticmethod
    def get_env_checksums(bitbake_variables):
        checksums = [0, 0]

        offsets = Helpers.get_env_offsets(bitbake_variables)
        dev = bitbake_variables["MENDER_STORAGE_DEVICE"]

        run("dd if=%s of=env1.tmp bs=1 count=4 skip=%d" % (dev, offsets[0]))
        run("dd if=%s of=env2.tmp bs=1 count=4 skip=%d" % (dev, offsets[1]))

        get("env1.tmp")
        get("env2.tmp")
        run("rm -f env1.tmp env2.tmp")

        env = open("env1.tmp")
        checksums[0] = env.read()
        env.close()
        env = open("env2.tmp")
        checksums[1] = env.read()
        env.close()

        os.remove("env1.tmp")
        os.remove("env2.tmp")

        return checksums

@pytest.mark.usefixtures("qemu_running", "no_image_file", "setup_bbb", "bitbake_path")
class TestUpdates:

    def test_broken_image_update(self, bitbake_variables):

        if not env.host_string:
            # This means we are not inside execute(). Recurse into it!
            execute(self.test_broken_image_update, bitbake_variables)
            return

        (active_before, passive_before) = determine_active_passive_part(bitbake_variables)

        try:
            # Make a dummy/broken update
            subprocess.call("dd if=/dev/zero of=image.dat bs=1M count=0 seek=16", shell=True)
            subprocess.call("mender-artifact write rootfs-image -t %s -n test-update -u image.dat -o image.mender" % image_type, shell=True)
            put("image.mender", remote_path="/var/tmp/image.mender")
            run("mender -rootfs /var/tmp/image.mender")
            reboot()

            # Now qemu is auto-rebooted twice; once to boot the dummy image,
            # where it fails, and uboot auto-reboots a second time into the
            # original partition.

            output = run_after_connect("mount")

            # The update should have reverted to the original active partition,
            # since the image was bogus.
            assert(output.find(active_before) >= 0)
            assert(output.find(passive_before) < 0)

        finally:
            # Cleanup.
            os.remove("image.mender")
            os.remove("image.dat")

    def test_too_big_image_update(self):
        if not env.host_string:
            # This means we are not inside execute(). Recurse into it!
            execute(self.test_too_big_image_update)
            return

        try:
            # Make a too big update
            subprocess.call("dd if=/dev/zero of=image.dat bs=1M count=0 seek=1024", shell=True)
            subprocess.call("mender-artifact write rootfs-image -t %s -n test-update-too-big -u image.dat -o image-too-big.mender" % image_type, shell=True)
            put("image-too-big.mender", remote_path="/var/tmp/image-too-big.mender")
            output = run("mender -rootfs /var/tmp/image-too-big.mender ; echo 'ret_code=$?'")

            assert(output.find("no space left on device") >= 0)
            assert(output.find("ret_code=0") < 0)

        finally:
            # Cleanup.
            os.remove("image-too-big.mender")
            os.remove("image.dat")

    def test_network_based_image_update(self, successful_image_update_mender, bitbake_variables):
        http_server_location = pytest.config.getoption("--http-server")
        bbb = pytest.config.getoption("--bbb")

        if not env.host_string:
            # This means we are not inside execute(). Recurse into it!
            execute(self.test_network_based_image_update, successful_image_update_mender, bitbake_variables)
            return

        (active_before, passive_before) = determine_active_passive_part(bitbake_variables)

        if bbb:
            Helpers.upload_to_s3()
            http_server_location = "s3.amazonaws.com/mender/temp"
        else:
            http_server = subprocess.Popen(["python", "-m", "SimpleHTTPServer"])
            assert(http_server)

        try:
            run("mender -rootfs http://%s/successful_image_update.mender" % (http_server_location))
        finally:
            if not bbb:
                http_server.terminate()

        output = run("fw_printenv bootcount")
        assert(output == "bootcount=0")

        output = run("fw_printenv upgrade_available")
        assert(output == "upgrade_available=1")

        output = run("fw_printenv mender_boot_part")
        assert(output == "mender_boot_part=" + passive_before[-1:])

        reboot()

        run_after_connect("true")
        (active_after, passive_after) = determine_active_passive_part(bitbake_variables)

        # The OS should have moved to a new partition, since the image was fine.
        assert(active_after == passive_before)
        assert(passive_after == active_before)

        output = run("fw_printenv bootcount")
        assert(output == "bootcount=1")

        output = run("fw_printenv upgrade_available")
        assert(output == "upgrade_available=1")

        output = run("fw_printenv mender_boot_part")
        assert(output == "mender_boot_part=" + active_after[-1:])

        run("mender -commit")

        output = run("fw_printenv upgrade_available")
        assert(output == "upgrade_available=0")

        output = run("fw_printenv mender_boot_part")
        assert(output == "mender_boot_part=" + active_after[-1:])

        active_before = active_after
        passive_before = passive_after

        reboot()

        run_after_connect("true")
        (active_after, passive_after) = determine_active_passive_part(bitbake_variables)

        # The OS should have stayed on the same partition, since we committed.
        assert(active_after == active_before)
        assert(passive_after == passive_before)

    def test_redundant_uboot_env(self, successful_image_update_mender, bitbake_variables):
        """This tests a very specific scenario: Consider the following production
        scenario: You are currently running an update on rootfs partition
        B. Then you attempt another update, which happens to be broken (but you
        don't know that yet). This will put the update in rootfs partition
        A. However, just as U-Boot is about to switch to rootfs partition A,
        using `upgrade_available=1` (and hence triggering bootlimit), the device
        loses power. This causes the stored U-Boot environment to become
        corrupt. On the next boot, U-Boot detects this and reverts to its built
        in environment instead.

        But this is a problem: The default environment will boot from rootfs
        partition A, which contains a broken update. And since U-Boot at this
        point doesn't know that an update was in progress, it will not attempt
        to boot from anywhere else (`upgrade_available=0`). Hence the device is
        bricked.

        This is what a redundant U-Boot environment is supposed to protect
        against by always providing two copies of the stored environment, and
        guaranteeing that at least one of them is always valid.

        In a test we cannot pull the power from the device reliably, but it's
        quite easy to simulate the situation by setting up the above scenario,
        and then corrupting the environment manually with a file write.

        """

        if not env.host_string:
            # This means we are not inside execute(). Recurse into it!
            execute(self.test_redundant_uboot_env, successful_image_update_mender, bitbake_variables)
            return

        (active, passive) = determine_active_passive_part(bitbake_variables)

        if active != bitbake_variables["MENDER_ROOTFS_PART_B"]:
            # We are not running the secondary partition. This is a requirement
            # for this test to test the correct scenario. Do a full update, so
            # that we end up on the right partition. Run the full update test to
            # correct this. If running all the tests in order with a fresh
            # build, the correct partition will usually be selected already.
            self.test_network_based_image_update(successful_image_update_mender, bitbake_variables)

            (active, passive) = determine_active_passive_part(bitbake_variables)
            assert(active == bitbake_variables["MENDER_ROOTFS_PART_B"])

        # Make a note of the checksums of each environment. We use this later to
        # determine which one changed.
        old_checksums = Helpers.get_env_checksums(bitbake_variables)

        orig_env = run("fw_printenv")

        try:
            # Make a dummy/broken update
            subprocess.call("dd if=/dev/zero of=image.dat bs=1M count=0 seek=8", shell=True)
            subprocess.call("mender-artifact write rootfs-image -t %s -n test-update -u image.dat -o image.mender" % image_type, shell=True)
            put("image.mender", remote_path="/var/tmp/image.mender")
            run("mender -rootfs /var/tmp/image.mender")

            new_checksums = Helpers.get_env_checksums(bitbake_variables)

            # Exactly one checksum should be different.
            assert(old_checksums[0] == new_checksums[0] or old_checksums[1] == new_checksums[1])
            assert(old_checksums[0] != new_checksums[0] or old_checksums[1] != new_checksums[1])

            if old_checksums[0] != new_checksums[0]:
                to_corrupt = 0
            elif old_checksums[1] != new_checksums[1]:
                to_corrupt = 1

            offsets = Helpers.get_env_offsets(bitbake_variables)

            # Now manually corrupt the environment.
            # A few bytes should do it!
            run("dd if=/dev/zero of=%s bs=1 count=64 seek=%d"
                % (bitbake_variables["MENDER_STORAGE_DEVICE"], offsets[to_corrupt]))
            run("sync")

            # Check atomicity of Mender environment update: The contents of the
            # environment before the update should be identical to the
            # environment we get if we update, and then corrupt the new
            # environment. If it's not identical, it's an indication that there
            # were intermediary steps. This is important to avoid so that the
            # environment is not in a half updated state.
            new_env = run("fw_printenv")
            assert orig_env == new_env

            reboot()

            # We should have recovered.
            run_after_connect("true")

            # And we should be back at the second rootfs partition.
            (active, passive) = determine_active_passive_part(bitbake_variables)
            assert(active == bitbake_variables["MENDER_ROOTFS_PART_B"])

        finally:
            # Cleanup.
            os.remove("image.mender")
            os.remove("image.dat")
