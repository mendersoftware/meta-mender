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

from fabric.api import *

import json
import os
import pytest
import shutil
import subprocess
import tempfile

# Make sure common is imported after fabric, because we override some functions.
from common import *


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

    @staticmethod
    def corrupt_middle_byte(fd):
        # Corrupt the middle byte in the contents.
        middle = int(os.fstat(fd.fileno()).st_size / 2)
        fd.seek(middle)
        middle_byte = int(fd.read(1).encode("hex"), base=16)
        fd.seek(middle)
        # Flip lowest bit.
        fd.write("%c" % (middle_byte ^ 0x1))

class SignatureCase:
    label = ""
    signature = False
    signature_ok = False
    key = False
    key_type = ""
    checksum_ok = True
    header_checksum_ok = True

    update_written = False
    success = True

    def __init__(self,
                 label,
                 signature,
                 signature_ok,
                 key,
                 key_type,
                 checksum_ok,
                 header_checksum_ok,
                 update_written,
                 artifact_version,
                 success):
        self.label = label
        self.signature = signature
        self.signature_ok = signature_ok
        self.key = key
        self.key_type = key_type
        self.checksum_ok = checksum_ok
        self.header_checksum_ok = header_checksum_ok
        self.update_written = update_written
        self.artifact_version = artifact_version
        self.success = success

@pytest.mark.usefixtures("no_image_file", "setup_board", "bitbake_path")
class TestUpdates:

    @pytest.mark.min_mender_version('1.0.0')
    def test_broken_image_update(self, bitbake_variables):

        if not env.host_string:
            # This means we are not inside execute(). Recurse into it!
            execute(self.test_broken_image_update, bitbake_variables)
            return

        (active_before, passive_before) = determine_active_passive_part(bitbake_variables)

        image_type = bitbake_variables["MACHINE"]

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

    @pytest.mark.min_mender_version('1.0.0')
    def test_too_big_image_update(self, bitbake_variables):
        if not env.host_string:
            # This means we are not inside execute(). Recurse into it!
            execute(self.test_too_big_image_update, bitbake_variables)
            return

        image_type = bitbake_variables["MACHINE"]

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

    @pytest.mark.min_mender_version('1.0.0')
    def test_network_based_image_update(self, successful_image_update_mender, bitbake_variables):
        http_server_location = pytest.config.getoption("--http-server")
        use_s3 = pytest.config.getoption("--use-s3")
        board = pytest.config.getoption("--board-type")

        if not env.host_string:
            # This means we are not inside execute(). Recurse into it!
            execute(self.test_network_based_image_update, successful_image_update_mender, bitbake_variables)
            return

        (active_before, passive_before) = determine_active_passive_part(bitbake_variables)

        if board or use_s3:
            Helpers.upload_to_s3()
            s3_address = pytest.config.getoption("--s3-address")
            http_server_location = "{}/mender/temp".format(s3_address)
        else:
            http_server = subprocess.Popen(["python", "-m", "SimpleHTTPServer"])
            assert(http_server)

        try:
            output = run("mender -rootfs http://%s/successful_image_update.mender" % (http_server_location))
        finally:
            print("output from rootfs update: ", output)
            if not board and not use_s3:
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

    @pytest.mark.parametrize("sig_case",
                             [SignatureCase(label="Not signed, key not present, version 1",
                                            signature=False,
                                            signature_ok=False,
                                            key=False,
                                            key_type=None,
                                            checksum_ok=True,
                                            header_checksum_ok=True,
                                            update_written=True,
                                            artifact_version=1,
                                            success=True),
                              SignatureCase(label="Not signed, key not present",
                                            signature=False,
                                            signature_ok=False,
                                            key=False,
                                            key_type=None,
                                            checksum_ok=True,
                                            header_checksum_ok=True,
                                            update_written=True,
                                            artifact_version=None,
                                            success=True),
                              SignatureCase(label="RSA, Correctly signed, key present",
                                            signature=True,
                                            signature_ok=True,
                                            key=True,
                                            key_type="RSA",
                                            checksum_ok=True,
                                            header_checksum_ok=True,
                                            update_written=True,
                                            artifact_version=None,
                                            success=True),
                              SignatureCase(label="RSA, Incorrectly signed, key present",
                                            signature=True,
                                            signature_ok=False,
                                            key=True,
                                            key_type="RSA",
                                            checksum_ok=True,
                                            header_checksum_ok=True,
                                            update_written=False,
                                            artifact_version=None,
                                            success=False),
                              SignatureCase(label="RSA, Correctly signed, key not present",
                                            signature=True,
                                            signature_ok=True,
                                            key=False,
                                            key_type="RSA",
                                            checksum_ok=True,
                                            header_checksum_ok=True,
                                            update_written=True,
                                            artifact_version=None,
                                            success=True),
                              SignatureCase(label="RSA, Not signed, key present",
                                            signature=False,
                                            signature_ok=False,
                                            key=True,
                                            key_type="RSA",
                                            checksum_ok=True,
                                            header_checksum_ok=True,
                                            update_written=False,
                                            artifact_version=None,
                                            success=False),
                              SignatureCase(label="RSA, Not signed, key present, version 1",
                                            signature=False,
                                            signature_ok=False,
                                            key=True,
                                            key_type="RSA",
                                            checksum_ok=True,
                                            header_checksum_ok=True,
                                            update_written=False,
                                            artifact_version=1,
                                            success=False),
                              SignatureCase(label="RSA, Correctly signed, but checksum wrong, key present",
                                            signature=True,
                                            signature_ok=True,
                                            key=True,
                                            key_type="RSA",
                                            checksum_ok=False,
                                            header_checksum_ok=True,
                                            update_written=True,
                                            artifact_version=None,
                                            success=False),
                              SignatureCase(label="EC, Correctly signed, key present",
                                            signature=True,
                                            signature_ok=True,
                                            key=True,
                                            key_type="EC",
                                            checksum_ok=True,
                                            header_checksum_ok=True,
                                            update_written=True,
                                            artifact_version=None,
                                            success=True),
                              SignatureCase(label="EC, Incorrectly signed, key present",
                                            signature=True,
                                            signature_ok=False,
                                            key=True,
                                            key_type="EC",
                                            checksum_ok=True,
                                            header_checksum_ok=True,
                                            update_written=False,
                                            artifact_version=None,
                                            success=False),
                              SignatureCase(label="EC, Correctly signed, key not present",
                                            signature=True,
                                            signature_ok=True,
                                            key=False,
                                            key_type="EC",
                                            checksum_ok=True,
                                            header_checksum_ok=True,
                                            update_written=True,
                                            artifact_version=None,
                                            success=True),
                              SignatureCase(label="EC, Not signed, key present",
                                            signature=False,
                                            signature_ok=False,
                                            key=True,
                                            key_type="EC",
                                            checksum_ok=True,
                                            header_checksum_ok=True,
                                            update_written=False,
                                            artifact_version=None,
                                            success=False),
                              SignatureCase(label="EC, Not signed, key present, version 1",
                                            signature=False,
                                            signature_ok=False,
                                            key=True,
                                            key_type="EC",
                                            checksum_ok=True,
                                            header_checksum_ok=True,
                                            update_written=False,
                                            artifact_version=1,
                                            success=False),
                              SignatureCase(label="EC, Correctly signed, but checksum wrong, key present",
                                            signature=True,
                                            signature_ok=True,
                                            key=True,
                                            key_type="EC",
                                            checksum_ok=False,
                                            header_checksum_ok=True,
                                            update_written=True,
                                            artifact_version=None,
                                            success=False),
                              SignatureCase(label="EC, Correctly signed, but header does not match checksum, key present",
                                            signature=True,
                                            signature_ok=True,
                                            key=True,
                                            key_type="EC",
                                            checksum_ok=True,
                                            header_checksum_ok=False,
                                            update_written=False,
                                            artifact_version=None,
                                            success=False),
                             ])
    @pytest.mark.min_mender_version('1.1.0')
    def test_signed_updates(self, sig_case, bitbake_path, bitbake_variables):
        """Test various combinations of signed and unsigned, present and non-
        present verification keys."""

        if not env.host_string:
            # This means we are not inside execute(). Recurse into it!
            execute(self.test_signed_updates, sig_case, bitbake_path, bitbake_variables)
            return

        # mmc mount points are named: /dev/mmcblk0p1
        # ubi volumes are named: ubi0_1
        (active, passive) = determine_active_passive_part(bitbake_variables)
        if passive.startswith('ubi'):
            passive = '/dev/' + passive

        # Generate "update" appropriate for this test case.
        # Cheat a little. Instead of spending a lot of time on a lot of reboots,
        # just verify that the contents of the update are correct.
        new_content = sig_case.label
        with open("image.dat", "w") as fd:
            fd.write(new_content)

        artifact_args = ""

        # Generate artifact with or without signature.
        if sig_case.signature:
            artifact_args += " -k %s" % signing_key(sig_case.key_type).private

        # Generate artifact with specific version. None means default.
        if sig_case.artifact_version is not None:
            artifact_args += " -v %d" % sig_case.artifact_version

        if sig_case.key_type:
            sig_key = signing_key(sig_case.key_type)
        else:
            sig_key = None

        image_type = bitbake_variables["MACHINE"]

        subprocess.check_call("mender-artifact write rootfs-image %s -t %s -n test-update -u image.dat -o image.mender"
                              % (artifact_args, image_type), shell=True)

        # If instructed to, corrupt the signature and/or checksum.
        if (sig_case.signature and not sig_case.signature_ok) or not sig_case.checksum_ok or not sig_case.header_checksum_ok:
            tar = subprocess.check_output(["tar", "tf", "image.mender"])
            tar_list = tar.split()
            tmpdir = tempfile.mkdtemp()
            try:
                shutil.copy("image.mender", os.path.join(tmpdir, "image.mender"))
                cwd = os.open(".", os.O_RDONLY)
                os.chdir(tmpdir)
                try:
                    tar = subprocess.check_output(["tar", "xf", "image.mender"])
                    if not sig_case.signature_ok:
                        # Corrupt signature.
                        with open("manifest.sig", "r+") as fd:
                            Helpers.corrupt_middle_byte(fd)
                    if not sig_case.checksum_ok:
                        os.chdir("data")
                        try:
                            data_list = subprocess.check_output(["tar", "tzf", "0000.tar.gz"])
                            data_list = data_list.split()
                            subprocess.check_call(["tar", "xzf", "0000.tar.gz"])
                            # Corrupt checksum by changing file slightly.
                            with open("image.dat", "r+") as fd:
                                Helpers.corrupt_middle_byte(fd)
                                # Need to update the expected content in this case.
                                fd.seek(0)
                                new_content = fd.read()
                            # Pack it up again in same order.
                            os.remove("0000.tar.gz")
                            subprocess.check_call(["tar", "czf", "0000.tar.gz"] + data_list)
                            for data_file in data_list:
                                os.remove(data_file)
                        finally:
                            os.chdir("..")

                    if not sig_case.header_checksum_ok:
                        data_list = subprocess.check_output(["tar", "tzf", "header.tar.gz"])
                        data_list = data_list.split()
                        subprocess.check_call(["tar", "xzf", "header.tar.gz"])
                        # Corrupt checksum by changing file slightly.
                        with open("headers/0000/files", "a") as fd:
                            # Some extra data to corrupt the header checksum,
                            # but still valid JSON.
                            fd.write(" ")
                        # Pack it up again in same order.
                        os.remove("header.tar.gz")
                        subprocess.check_call(["tar", "czf", "header.tar.gz"] + data_list)
                        for data_file in data_list:
                            os.remove(data_file)

                    # Make sure we put it back in the same order.
                    os.remove("image.mender")
                    subprocess.check_call(["tar", "cf", "image.mender"] + tar_list)
                finally:
                    os.fchdir(cwd)
                    os.close(cwd)

                shutil.move(os.path.join(tmpdir, "image.mender"), "image.mender")

            finally:
                shutil.rmtree(tmpdir, ignore_errors=True)

        put("image.mender")
        try:
            # Update key configuration on device.
            run("cp /etc/mender/mender.conf /etc/mender/mender.conf.bak")
            get("mender.conf", remote_path="/etc/mender")
            with open("mender.conf") as fd:
                config = json.load(fd)
            if sig_case.key:
                config['ArtifactVerifyKey'] = "/etc/mender/%s" % os.path.basename(sig_key.public)
                put(sig_key.public, remote_path="/etc/mender")
            else:
                if config.get('ArtifactVerifyKey'):
                    del config['ArtifactVerifyKey']
            with open("mender.conf", "w") as fd:
                json.dump(config, fd)
            put("mender.conf", remote_path="/etc/mender")
            os.remove("mender.conf")

            # Start by writing known "old" content in the partition.
            old_content = "Preexisting partition content"
            if 'ubi' in passive:
                # ubi volumes cannot be directly written to, we have to use
                # ubiupdatevol
                run('echo "%s" | dd of=/tmp/update.tmp && ' \
                    'ubiupdatevol %s /tmp/update.tmp; ' \
                    'rm -f /tmp/update.tmp' % (old_content, passive))
            else:
                run('echo "%s" | dd of=%s' % (old_content, passive))

            with settings(warn_only=True):
                result = run("mender -rootfs image.mender")

            if sig_case.success:
                if result.return_code != 0:
                    pytest.fail("Update failed when it should have succeeded: %s, Output: %s" % (sig_case.label, result))
            else:
                if result.return_code == 0:
                    pytest.fail("Update succeeded when it should not have: %s, Output: %s" % (sig_case.label, result))

            if sig_case.update_written:
                expected_content = new_content
            else:
                expected_content = old_content

            content = run("dd if=%s bs=%d count=1"
                          % (passive, len(expected_content)))
            assert content == expected_content, "Case: %s" % sig_case.label

        finally:
            # Reset environment to what it was.
            run("fw_setenv mender_boot_part %s" % active[-1:])
            run("fw_setenv update_available 0")
            run("mv /etc/mender/mender.conf.bak /etc/mender/mender.conf")
            if sig_key:
                run("rm -f /etc/mender/%s" % os.path.basename(sig_key.public))


    @pytest.mark.only_for_machine('vexpress-qemu')
    @pytest.mark.min_mender_version('1.0.0')
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

        image_type = bitbake_variables["MACHINE"]

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
