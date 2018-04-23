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

        # SHA from poky repository, limited by date.
        poky_rev = subprocess.check_output("git log -n1 --format=%%H --after=%d.days.ago HEAD" % days_to_be_old, shell=True,
                                           cwd=os.path.join(os.environ['BUILDDIR'], "..")).strip()
        if poky_rev:
            print("Running test_uboot_compile because poky commit is more recent than %d days." % days_to_be_old)
            return

        # SHA from meta-mender repository, limited by date.
        meta_mender_uboot_rev = subprocess.check_output(("git log -n1 --format=%%H --after=%d.days.ago HEAD -- "
                                                         + "../../meta-mender-core/recipes-bsp/u-boot")
                                                        % days_to_be_old,
                                                        shell=True).strip()
        if meta_mender_uboot_rev:
            print("Running test_uboot_compile because u-boot in meta-mender has been modified more recently than %d days ago." % days_to_be_old)
            return

        # SHA from meta-mender repository, not limited by date.
        meta_mender_uboot_rev = subprocess.check_output("git log -n1 --format=%H HEAD -- "
                                                         + "../../meta-mender-core/recipes-bsp/u-boot",
                                                        shell=True).strip()
        for remote in subprocess.check_output(["git", "remote"]).split():
            url = subprocess.check_output("git config --get remote.%s.url" % remote, shell=True)
            if "mendersoftware" in url:
                upstream_remote = remote
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

    def board_not_arm(self, bitbake_variables, config):
        with open(os.path.join(bitbake_variables['S'], "configs", config)) as fd:
            for line in fd.readlines():
                line = line.strip()
                if line.startswith("CONFIG_TARGET_") and line.endswith("=y"):
                    # Extract target name.
                    target = line.split("=", 2)[0]
                    # Remove "CONFIG_" prefix.
                    target = target[len("CONFIG_"):]
                    break
            else:
                # We don't know, so we return that it's not definitely not ARM
                # (yes, double negatives...)
                return False

        # Look for that config value inside Kconfig files that are not in arm
        # directory.
        for walk in os.walk(os.path.join(bitbake_variables['S'], "arch"), topdown=True):
            walk[1][:] = [dir for dir in walk[1] if dir != "arm"]

            walk[2][:] = [file for file in walk[2] if file == "Kconfig"]

            for file in walk[2]:
                with open(os.path.join(walk[0], file)) as fd:
                    if re.search("^config *%s *$" % target, fd.read(), re.MULTILINE):
                        # Found the target in a non-arm directory. This is not
                        # an ARM board.
                        return True

        return False

    def collect_and_prepare_boards_to_test(self, bitbake_variables, env):
        # Find all the boards we need to test for the configuration in question.
        # For vexpress-qemu, we test all SD-based boards, for vexpress-qemu-flash
        # we test all Flash based boards.
        machine = bitbake_variables["MACHINE"]
        available_configs = sorted(os.listdir(os.path.join(bitbake_variables['S'], "configs")))
        configs_to_test = []
        for config in available_configs:
            if not config.endswith("_defconfig"):
                continue

            if self.board_not_arm(bitbake_variables, config):
                continue

            mtdids = None
            mtdparts = None
            extra_patch_args = ""
            with open(os.path.join(bitbake_variables['S'], "configs", config)) as fd:
                for line in fd.readlines():
                    line = line.strip()
                    if line.startswith("CONFIG_MTDPARTS_DEFAULT="):
                        mtdparts = line.split("=", 2)[1]
                    elif line.startswith("CONFIG_MTDIDS_DEFAULT="):
                        mtdids = line.split("=", 2)[1]

            if mtdparts:
                # Assume Flash board.

                if machine != "vexpress-qemu-flash":
                    continue

                if mtdids and mtdids.startswith("\"nand"):
                    extra_patch_args = "--ubi --mtdids=nand=10000000.flash --mtdparts=10000000.flash:512k(u-boot),255m(ubi)"
                elif mtdids and mtdids.startswith("\"onenand"):
                    extra_patch_args = "--ubi --mtdids=onenand=20000000.flash --mtdparts=20000000.flash:512k(u-boot),255m(ubi)"
                elif mtdids and mtdids.startswith("\"nor"):
                    extra_patch_args = "--ubi --mtdids=nor=30000000.flash --mtdparts=30000000.flash:512k(u-boot),255m(ubi)"
                else:
                    # If board lacks mtdids, or it is unrecognized, treat it as a failed board.
                    with open(os.path.join(env['LOGS'], config), "w") as fd:
                        fd.write("test_uboot_compile: Unrecognized mtdids: %s\n" % mtdids)
                        fd.write("AutoPatchFailed\n")
            else:
                # Assume block storage board.
                if machine != "vexpress-qemu":
                    continue
                extra_patch_args = ""

            configs_to_test.append(os.path.join(env['LOGS'], config))
            # Provide arguments for the board that the patching process will use.
            with open(os.path.join(env['LOGS'], "%s.params" % config), "w") as fd:
                fd.write(extra_patch_args)

        return configs_to_test

    @pytest.mark.min_mender_version('1.0.0')
    def test_uboot_compile(self, bitbake_env, bitbake_variables):
        """Test that our automatic patching of U-Boot still successfully builds
        the expected number of boards."""

        # No need to test this on non-vexpress-qemu. It is a very resource
        # consuming test, and it is identical on all boards, since it internally
        # tests all boards.
        machine = bitbake_variables["MACHINE"]
        if not machine.startswith("vexpress-qemu"):
            pytest.skip("Skipping test on non-vexpress-qemu platforms")

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
        if os.path.exists(env['LOGS']):
            print("WARNING: %s already exists. Will use cached logs from there. Recreate to reset." % env['LOGS'])
        else:
            os.mkdir(env['LOGS'])

        configs_to_test = self.collect_and_prepare_boards_to_test(bitbake_variables, env)

        env['BOARD_LOGS'] = " ".join(configs_to_test)

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
                if not file.endswith("_defconfig"):
                    continue

                total += 1
                with open(os.path.join(env['LOGS'], file)) as fd:
                    if "AutoPatchFailed\n" in fd.readlines():
                        failed += 1

            assert total == len(configs_to_test), "Number of logs do not match the number of boards we tested? Should not happen"

            if machine == "vexpress-qemu":
                # PLEASE UPDATE the version you used to find this number if you update it.
                # From version: v2017.09
                measured_failed_ratio = 747.0 / 1176.0
            elif machine == "vexpress-qemu-flash":
                # PLEASE UPDATE the version you used to find this number if you update it.
                # From version: v2018.01
                measured_failed_ratio = 47.0 / 156.0

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
