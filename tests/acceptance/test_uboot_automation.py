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
    @staticmethod
    def parallel_job_count():
        # Due to our extensive copying of sources, we are constrained by both
        # I/O and CPU during compiling. Therefore we use the RAM disk to to
        # store the temporary sources. So pick a parallel job number that
        # doesn't exhaust neither memory nor CPU.

        # Rough estimate, we assume that each source directory needs
        # approximately 1G, and that we can use half of the memory for that.
        with open("/proc/meminfo") as fd:
            for line in fd.readlines():
                match = re.match("^MemTotal:\s+([0-9]+)\s*kB", line)
                if match:
                    memory_kb = int(match.group(1))
                    break
        memory_jobs = int(memory_kb / 2 / 1048576)

        return min(memory_jobs, multiprocessing.cpu_count())

    def check_if_should_run(self):
        # The logic here is this:
        #
        # * If any commit in poky, or a commit touching
        #   meta-mender/meta-mender-core/u-boot, is more recent than a certain
        #   time, carry out the test.
        #
        # * If a commit touching meta-mender/meta-mender-core/u-boot is older
        #   than the given time, but no upstream branch contains it, carry out
        #   the test.
        #
        # * Else, skip the test.
        #
        # The rationale is that the test is extremely time consuming, and
        # therefore we should try to avoid it if the branch has been stable for
        # a while. We include the second conditional above so that PRs are
        # always checked, even if they are old.

        # Number of days that must pass for the branch to be considered stable.
        days_to_be_old = 7

        # Find the repository directories we need
        [ poky_dir, meta_mender_core_dir, rest ] = subprocess.check_output(
            "bitbake-layers show-layers | awk '$1~/(^meta$|^meta-mender-core$)/ {print $2}' | xargs -n 1 dirname",
            cwd=os.environ['BUILDDIR'], shell=True).split("\n")

        # SHA from poky repository, limited by date.
        poky_rev = subprocess.check_output("git log -n1 --format=%%H --after=%d.days.ago HEAD" % days_to_be_old, shell=True,
                                           cwd=poky_dir).strip()
        if poky_rev:
            print("Running test_uboot_compile because poky commit is more recent than %d days." % days_to_be_old)
            return

        # SHA from meta-mender repository, limited by date.
        meta_mender_uboot_rev = subprocess.check_output(("git log -n1 --format=%%H --after=%d.days.ago HEAD -- "
                                                         + "recipes-bsp/u-boot")
                                                        % days_to_be_old,
                                                        cwd=meta_mender_core_dir,
                                                        shell=True).strip()
        if meta_mender_uboot_rev:
            print("Running test_uboot_compile because u-boot in meta-mender has been modified more recently than %d days ago." % days_to_be_old)
            return

        # SHA from meta-mender repository, not limited by date.
        meta_mender_uboot_rev = subprocess.check_output("git log -n1 --format=%H HEAD -- "
                                                        + "recipes-bsp/u-boot",
                                                        cwd=meta_mender_core_dir,
                                                        shell=True).strip()
        for remote in subprocess.check_output(["git", "remote"]).split():
            url = subprocess.check_output("git config --get remote.%s.url" % remote, shell=True)
            if "mendersoftware" in url:
                upstream_remote = remote
                break
        else:
            pytest.fail("Upstream remote not found! Should not happen.")

        contained_in = subprocess.check_output("git branch -r --contains %s" % meta_mender_uboot_rev, shell=True).split()
        is_upstream = False
        for branch in contained_in:
            if branch.startswith("%s/" % upstream_remote) and not branch.startswith("%s/pull/" % upstream_remote):
                is_upstream = True
                break

        if not is_upstream:
            print("Running test_uboot_compile because meta-mender commit is not upstream yet.")
            return

        msg = "Skipping test_uboot_compile because u-boot commits are old and already upstream."
        print(msg)
        pytest.skip(msg)


    # No need to test this on non-vexpress-qemu. It is a very resource consuming
    # test, and it is identical on all boards, since it internally tests all
    # boards.
    @pytest.mark.only_for_machine('vexpress-qemu')
    @pytest.mark.min_mender_version('1.0.0')
    def test_uboot_compile(self, bitbake_path):
        """Test that our automatic patching of U-Boot still successfully builds
        the expected number of boards."""

        # This is a slow running test. Skip if appropriate.
        self.check_if_should_run()

        for task in ["do_provide_mender_defines", "prepare_recipe_sysroot"]:
            subprocess.check_call("cd %s && bitbake -c %s u-boot" % (os.environ['BUILDDIR'], task),
                                  shell=True)
        bitbake_variables = get_bitbake_variables("u-boot")

        shutil.rmtree("/dev/shm/test_uboot_compile", ignore_errors=True)

        env = copy.copy(os.environ)
        env['UBOOT_SRC'] = bitbake_variables['S']
        env['TESTS_DIR'] = os.getcwd()
        env['LOGS'] = os.path.join(os.getcwd(), "test_uboot_compile-logs")
        try:
            sanitized_makeflags = bitbake_variables['EXTRA_OEMAKE']
            sanitized_makeflags = sanitized_makeflags.replace("\\\"", "\"")
            sanitized_makeflags = re.sub(" +", " ", sanitized_makeflags)
            # Compile all boards. The reason for using a makefile is to get easy
            # parallelization.
            subprocess.check_call("make -j %d -f %s TMP=/dev/shm/test_uboot_compile %s"
                                  % (self.parallel_job_count(),
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

        finally:
            shutil.rmtree("/dev/shm/test_uboot_compile", ignore_errors=True)

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
        add_to_local_conf(prepared_test_build, 'PREFERRED_RPROVIDER_u-boot = "u-boot-testing"')
        run_bitbake(prepared_test_build)

        new_rootfs = latest_build_artifact(prepared_test_build['build_dir'], "core-image*.ext[234]")
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
    def test_save_mender_auto_configured_patch(self, bitbake_variables, prepared_test_build):
        """Test that we can invoke the save_mender_auto_configured_patch task,
        and that it produces a patch file."""

        if "mender-uboot" not in bitbake_variables['DISTRO_FEATURES']:
            pytest.skip("Only relevant for U-Boot configurations")

        bitbake_variables = get_bitbake_variables("u-boot", env_setup=prepared_test_build['env_setup'])

        # Only run if auto-configuration is on.
        if bitbake_variables['MENDER_UBOOT_AUTO_CONFIGURE'] == "0":
            pytest.skip("Test is not applicable when MENDER_UBOOT_AUTO_CONFIGURE is off")

        run_bitbake(prepared_test_build, "-c save_mender_auto_configured_patch u-boot")

        with open(os.path.join(bitbake_variables['WORKDIR'], 'mender_auto_configured.patch')) as fd:
            content = fd.read()
            # Make sure it looks like a patch.
            assert "---" in content
            assert "+++" in content
