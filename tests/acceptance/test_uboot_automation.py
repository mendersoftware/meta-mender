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

import copy
import multiprocessing
import os
import re
import shutil
import subprocess

# Make sure common is imported after fabric, because we override some functions.
from common import *

class TestUbootAutomation:
    def revision_already_checked(self):
        # ----------------------------------------------------------------------
        # Update these two to skip the check.
        expected_poky_rev = "21ba45aa77e4d43a93cd96d859707a4758e8b64b"
        expected_meta_mender_uboot_rev = "4d246c2c6d8b7b79b54f2ffd5ba087e5d2fb7467"
        # ----------------------------------------------------------------------

        # SHA from poky repository.
        poky_rev = subprocess.check_output("git rev-parse HEAD", shell=True,
                                           cwd=os.path.join(os.environ['BUILDDIR'], "..")).strip()
        # SHA from meta-mender repository.
        meta_mender_uboot_rev = subprocess.check_output("git rev-list -n1 HEAD -- ../../meta-mender-core/recipes-bsp/u-boot",
                                                        shell=True).strip()
        if expected_poky_rev != poky_rev or expected_meta_mender_uboot_rev != meta_mender_uboot_rev:
            print("""Need to run test_uboot_compile. Used these SHAs for comparison:

poky_rev = %s
meta_mender_uboot_rev = %s

If this combination has been verified to pass, you can set the two variables:

expected_poky_rev
expected_meta_mender_uboot_rev

to the values above. This will cause the test to be skipped until the SHAs
change."""
                  % (poky_rev, meta_mender_uboot_rev))
            return False

        return True

    # No need to test this on non-vexpress-qemu. It is a very resource consuming
    # test, and it is identical on all boards, since it internally tests all
    # boards.
    @pytest.mark.only_for_machine('vexpress-qemu')
    @pytest.mark.min_mender_version('1.0.0')
    def test_uboot_compile(self, bitbake_path):
        """Test that our automatic patching of U-Boot still successfully builds
        the expected number of boards."""

        # THIS IS A SLOW RUNNING TEST!
        # Use the revision inside the function below to optimize and skip
        # checking based on version.
        if self.revision_already_checked():
            pytest.skip("Revision of poky and u-boot already checked")

        for task in ["do_provide_mender_defines", "prepare_recipe_sysroot"]:
            subprocess.check_call("cd %s && bitbake -c %s u-boot" % (os.environ['BUILDDIR'], task),
                                  shell=True)
        bitbake_variables = get_bitbake_variables("u-boot")

        env = copy.copy(os.environ)
        env['UBOOT_SRC'] = bitbake_variables['S']
        env['TESTS_DIR'] = os.getcwd()
        env['LOGS'] = os.path.join(os.getcwd(), "test_uboot_compile-logs")
        sanitized_makeflags = bitbake_variables['EXTRA_OEMAKE']
        sanitized_makeflags = sanitized_makeflags.replace("\\\"", "\"")
        sanitized_makeflags = re.sub(" +", " ", sanitized_makeflags)
        # Compile all boards. The reason for using a makefile is to get easy
        # parallelization.
        subprocess.check_call("make -j %d -f %s %s" % (multiprocessing.cpu_count() + 1,
                                                       os.path.join(env['TESTS_DIR'],
                                                                    "files/Makefile.test_uboot_automation"),
                                                       sanitized_makeflags),
                              shell=True,
                              env=env,
                              stderr=subprocess.STDOUT)

        # Now check that the ratio of compiled boards is as expected. This
        # number may change over time as U-Boot changes, but big discrepancies
        # should be checked out.
        failed = 0.0
        total = 0.0
        for file in os.listdir(env['LOGS']):
            total += 1
            with open(os.path.join(env['LOGS'], file)) as fd:
                if "AutoPatchFailed\n" in fd.readlines():
                    failed += 1

        # PLEASE UPDATE the version you used to find this number if you update it.
        # From version: v2017.09
        measured_failed_ratio = 747.0 / 1176.0

        # We tolerate a certain percentage discrepancy in either direction.
        tolerated_discrepancy = 0.1

        lower_bound = measured_failed_ratio * (1.0 - tolerated_discrepancy)
        upper_bound = measured_failed_ratio * (1.0 + tolerated_discrepancy)
        try:
            assert failed / total >= lower_bound, "Less boards failed than expected. Good? Or a mistake somewhere? Failed: %d, Total: %d" % (failed, total)
            assert failed / total <= upper_bound, "More boards failed than expected. Failed: %d, Total: %d" % (failed, total)
        except AssertionError:
            for file in os.listdir(env['LOGS']):
                with open(os.path.join(env['LOGS'], file)) as fd:
                    log = fd.readlines()
                    if "AutoPatchFailed\n" in log:
                        print("Last 50 lines of output from failed board: " + file)
                        print("".join(log[-50:]))
            raise

        shutil.rmtree(env['LOGS'])

    @pytest.mark.only_with_image('sdimg')
    @pytest.mark.min_mender_version('1.0.0')
    def test_auto_provided_fw_utils(self, prepared_test_build, latest_rootfs):
        """Test that we can provide our own custom U-Boot provider, and that
        this will trigger auto provision of the corresponding fw-utils."""

        subprocess.check_call(["debugfs", "-R", "dump /sbin/fw_setenv fw_setenv.tmp", latest_rootfs])

        try:
            with open("fw_setenv.tmp") as fd:
                # The vanilla version should not have our custom string.
                assert "TestStringThatMustOccur_Mender!#%&" not in fd.read(), "fw_setenv.tmp contains unexpected substring"
        finally:
            os.unlink("fw_setenv.tmp")

        add_to_local_conf(prepared_test_build, 'PREFERRED_PROVIDER_u-boot = "u-boot-testing"')
        run_bitbake(prepared_test_build)

        new_rootfs = latest_build_artifact(prepared_test_build['build_dir'], ".ext[234]")
        subprocess.check_call(["debugfs", "-R", "dump /sbin/fw_setenv fw_setenv.tmp", new_rootfs])

        try:
            with open("fw_setenv.tmp") as fd:
                # If we selected u-boot-testing as the U-Boot provider, fw-utils
                # should have followed and should also contain the special
                # substring which that version is patched with.
                assert "TestStringThatMustOccur_Mender!#%&" in fd.read(), "fw_setenv.tmp does not contain expected substring"
        finally:
            os.unlink("fw_setenv.tmp")

        # Reset local.conf.
        reset_local_conf(prepared_test_build)

        bitbake_vars = get_bitbake_variables("u-boot", env_setup=prepared_test_build['env_setup'])
        if bitbake_vars['MENDER_UBOOT_AUTO_CONFIGURE'] == "0":
            # The rest of the test is irrelevant if MENDER_UBOOT_AUTO_CONFIGURE
            # is already off.
            return

        add_to_local_conf(prepared_test_build, 'MENDER_UBOOT_AUTO_CONFIGURE_pn-u-boot = "0"')
        try:
            # Capture and discard output, it looks very ugly in the log.
            run_bitbake(prepared_test_build, capture=True)
            pytest.fail("Build should not succeed when MENDER_UBOOT_AUTO_CONFIGURE is turned off")
        except subprocess.CalledProcessError:
            pass

    @pytest.mark.min_mender_version('1.0.0')
    def test_save_mender_auto_configured_patch(self, prepared_test_build):
        """Test that we can invoke the save_mender_auto_configured_patch task,
        and that it produces a patch file."""

        bitbake_vars = get_bitbake_variables("u-boot", env_setup=prepared_test_build['env_setup'])

        # Only run if auto-configuration is on.
        if bitbake_vars['MENDER_UBOOT_AUTO_CONFIGURE'] == "0":
            pytest.skip("Test is not applicable when MENDER_UBOOT_AUTO_CONFIGURE is off")

        run_bitbake(prepared_test_build, "-c save_mender_auto_configured_patch u-boot")

        with open(os.path.join(bitbake_vars['WORKDIR'], 'mender_auto_configured.patch')) as fd:
            content = fd.read()
            # Make sure it looks like a patch.
            assert "---" in content
            assert "+++" in content
