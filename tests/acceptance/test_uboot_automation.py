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

import copy
import math
import multiprocessing
import os
import re
import shutil
import subprocess
import tempfile

import pytest

from utils.common import (
    build_image,
    bitbake_env_from,
    get_bitbake_variables,
    reset_build_conf,
    latest_build_artifact,
)


@pytest.mark.only_with_distro_feature("mender-uboot")
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
                match = re.match(r"^MemTotal:\s+([0-9]+)\s*kB", line)
                if match:
                    memory_kb = int(match.group(1))
                    break
        memory_jobs = int(memory_kb / 2 / 1048576)

        return min(memory_jobs, multiprocessing.cpu_count())

    @staticmethod
    def parallel_subjob_count():
        # Since memory can be the constraining factor on number of parallel
        # build directories (see comment for parallel_job_count), we should make
        # sure that each build directory uses enough cores to utilize all cores
        # total.
        job_count = TestUbootAutomation.parallel_job_count()
        cpu_count = multiprocessing.cpu_count()
        # Pick the smallest number that makes NUMBER * job_count >= cpu_count
        return int(math.ceil(float(cpu_count) / float(job_count)))

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
        [poky_dir, meta_mender_dir, rest] = (
            subprocess.check_output(
                "bitbake-layers show-layers | awk '$1~/(^meta$|^meta-mender-core$)/ {print $2}' | xargs -n 1 dirname",
                cwd=os.environ["BUILDDIR"],
                shell=True,
            )
            .decode()
            .split("\n")
        )

        # SHA from poky repository, limited by date.
        poky_rev = (
            subprocess.check_output(
                "git log -n1 --format=%%H --after=%d.days.ago HEAD" % days_to_be_old,
                shell=True,
                cwd=poky_dir,
            )
            .decode()
            .strip()
        )
        if poky_rev:
            print(
                "Running test_uboot_compile because poky commit is more recent than %d days."
                % days_to_be_old
            )
            return

        uboot_related_paths = [
            "meta-mender-core/recipes-bsp/u-boot",
            "tests/acceptance/test_uboot_automation.py",
            "tests/acceptance/files/Makefile.test_uboot_automation",
        ]

        for uboot_path in uboot_related_paths:
            path_to_check = os.path.join(meta_mender_dir, uboot_path)
            assert os.path.exists(path_to_check), (
                "%s does not exist in the repository. Should the list of paths be updated?"
                % path_to_check
            )

        # SHA from meta-mender repository, limited by date.
        meta_mender_uboot_rev = (
            subprocess.check_output(
                (
                    "git log -n1 --format=%%H --after=%d.days.ago HEAD -- "
                    + " ".join(uboot_related_paths)
                )
                % days_to_be_old,
                cwd=meta_mender_dir,
                shell=True,
            )
            .decode()
            .strip()
        )
        if meta_mender_uboot_rev:
            print(
                "Running test_uboot_compile because u-boot in meta-mender has been modified more recently than %d days ago."
                % days_to_be_old
            )
            return

        # SHA from meta-mender repository, not limited by date.
        meta_mender_uboot_rev = (
            subprocess.check_output(
                "git log -n1 --format=%H HEAD -- " + " ".join(uboot_related_paths),
                cwd=meta_mender_dir,
                shell=True,
            )
            .decode()
            .strip()
        )
        for remote in subprocess.check_output(["git", "remote"]).decode().split():
            url = subprocess.check_output(
                "git config --get remote.%s.url" % remote, shell=True
            ).decode()
            if "mendersoftware" in url:
                upstream_remote = remote
                break
        else:
            pytest.fail("Upstream remote not found! Should not happen.")

        contained_in = (
            subprocess.check_output(
                "git branch -r --contains %s" % meta_mender_uboot_rev, shell=True
            )
            .decode()
            .split()
        )
        is_upstream = False
        for branch in contained_in:
            if (
                branch.startswith("%s/" % upstream_remote)
                and not branch.startswith("%s/pull/" % upstream_remote)
                and not branch.startswith("%s/pr_" % upstream_remote)
            ):
                is_upstream = True
                break

        if not is_upstream:
            print(
                "Running test_uboot_compile because meta-mender commit is not upstream yet."
            )
            return

        msg = "Skipping test_uboot_compile because u-boot commits are old and already upstream."
        print(msg)
        pytest.skip(msg)

    def board_is_arm(self, srcdir, config):
        if config in ["xilinx_versal_virt_defconfig"]:
            # u-boot-v2019.01: There is some weird infinite loop in the conf
            # script of this particular board. Just mark it as "not ARM", which
            # will cause it to be skipped.
            return False

        print("Checking whether %s is an ARM board..." % config)
        subprocess.check_call("${MAKE:-make} %s" % config, cwd=srcdir, shell=True)
        with open(os.path.join(srcdir, ".config")) as fd:
            content = fd.read()
            # No ARM64 support at the moment.
            is_arm = "CONFIG_ARM=y\n" in content and "CONFIG_ARM64=y\n" not in content
            print("%s is %s" % (config, "ARM" if is_arm else "not ARM"))
            return is_arm

    def collect_and_prepare_boards_to_test(self, bitbake_variables, env):
        # Find all the boards we need to test for the configuration in question.
        # For vexpress-qemu, we test all SD-based boards, for vexpress-qemu-flash
        # we test all Flash based boards.

        # Use a temporary directory.
        with tempfile.TemporaryDirectory() as tmpdir:
            os.rmdir(tmpdir)
            shutil.copytree(bitbake_variables["S"], tmpdir)

            machine = bitbake_variables["MACHINE"]
            available_configs = sorted(os.listdir(os.path.join(tmpdir, "configs")))
            configs_to_test = []
            for config in available_configs:
                if not config.endswith("_defconfig"):
                    continue

                if not self.board_is_arm(tmpdir, config):
                    continue

                mtdids = None
                mtdparts = None
                with open(os.path.join(tmpdir, "configs", config)) as fd:
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

                else:
                    # Assume block storage board.
                    if machine != "vexpress-qemu":
                        continue

                configs_to_test.append(os.path.join(env["LOGS"], config))

            return configs_to_test

    @pytest.mark.min_mender_version("1.0.0")
    def test_uboot_compile(self, request, bitbake_variables):
        """Test that our automatic patching of U-Boot still successfully builds
        the expected number of boards."""

        with bitbake_env_from(request, "u-boot"):
            self.run_test_uboot_compile(request, bitbake_variables)

    def run_test_uboot_compile(self, request, bitbake_variables):
        # No need to test this on non-vexpress-qemu. It is a very resource
        # consuming test, and it is identical on all boards, since it internally
        # tests all boards.
        machine = bitbake_variables["MACHINE"]
        if not machine.startswith("vexpress-qemu"):
            pytest.skip("Skipping test on non-vexpress-qemu platforms")

        # This is a slow running test. Skip if appropriate.
        self.check_if_should_run()

        for task in ["do_provide_mender_defines", "prepare_recipe_sysroot"]:
            subprocess.check_call(
                "cd %s && bitbake -c %s u-boot" % (os.environ["BUILDDIR"], task),
                shell=True,
            )
        bitbake_variables = get_bitbake_variables(request, "u-boot")

        shutil.rmtree("/dev/shm/test_uboot_compile", ignore_errors=True)

        env = copy.copy(os.environ)
        env["UBOOT_SRC"] = bitbake_variables["S"]
        env["TESTS_DIR"] = os.getcwd()
        env["LOGS"] = os.path.join(os.getcwd(), "test_uboot_compile-logs")
        if os.path.exists(env["LOGS"]):
            print(
                "WARNING: %s already exists. Will use cached logs from there. Recreate to reset."
                % env["LOGS"]
            )
        else:
            os.mkdir(env["LOGS"])

        configs_to_test = self.collect_and_prepare_boards_to_test(
            bitbake_variables, env
        )

        env["BOARD_LOGS"] = " ".join(configs_to_test)

        try:
            sanitized_makeflags = bitbake_variables["EXTRA_OEMAKE"]
            sanitized_makeflags = sanitized_makeflags.replace('\\"', '"')
            sanitized_makeflags = re.sub(" +", " ", sanitized_makeflags)
            env["MAYBE_UBI"] = "--ubi" if machine == "vexpress-qemu-flash" else ""
            # Compile all boards. The reason for using a makefile is to get easy
            # parallelization.
            subprocess.check_call(
                "make -j %d -f %s SUBJOBCOUNT=-j%d TMP=/dev/shm/test_uboot_compile %s"
                % (
                    self.parallel_job_count(),
                    os.path.join(
                        env["TESTS_DIR"], "files/Makefile.test_uboot_automation"
                    ),
                    self.parallel_subjob_count(),
                    sanitized_makeflags,
                ),
                shell=True,
                env=env,
                stderr=subprocess.STDOUT,
            )

            # Now check that the ratio of compiled boards is as expected. This
            # number may change over time as U-Boot changes, but big discrepancies
            # should be checked out.
            failed = 0.0
            total = 0.0
            for file in os.listdir(env["LOGS"]):
                if not file.endswith("_defconfig"):
                    continue

                total += 1
                with open(os.path.join(env["LOGS"], file)) as fd:
                    if "AutoPatchFailed\n" in fd.readlines():
                        failed += 1

            assert total == len(
                configs_to_test
            ), "Number of logs do not match the number of boards we tested? Should not happen"

            if machine == "vexpress-qemu":
                # PLEASE UPDATE the version you used to find this number if you update it.
                # From version: v2020.01
                measured_failed_ratio = 57.0 / 561.0
            elif machine == "vexpress-qemu-flash":
                # PLEASE UPDATE the version you used to find this number if you update it.
                # From version: v2020.01
                measured_failed_ratio = 13.0 / 143.0

            # We tolerate a certain percentage discrepancy in either direction.
            tolerated_discrepancy = 0.1

            lower_bound = measured_failed_ratio * (1.0 - tolerated_discrepancy)
            upper_bound = measured_failed_ratio * (1.0 + tolerated_discrepancy)
            try:
                assert failed / total >= lower_bound, (
                    "Less boards failed than expected. Good? Or a mistake somewhere? Failed: %d, Total: %d"
                    % (failed, total)
                )
                assert failed / total <= upper_bound, (
                    "More boards failed than expected. Failed: %d, Total: %d"
                    % (failed, total)
                )
            except AssertionError:
                for file in os.listdir(env["LOGS"]):
                    with open(os.path.join(env["LOGS"], file)) as fd:
                        log = fd.readlines()
                        if "AutoPatchFailed\n" in log:
                            print("Last 50 lines of output from failed board: " + file)
                            print("".join(log[-50:]))
                raise

            shutil.rmtree(env["LOGS"])

        finally:
            shutil.rmtree("/dev/shm/test_uboot_compile", ignore_errors=True)

    @pytest.mark.only_with_image("sdimg")
    @pytest.mark.min_mender_version("1.0.0")
    def test_auto_provided_fw_utils(
        self, request, prepared_test_build, latest_rootfs, bitbake_image
    ):
        """Test that we can provide our own custom U-Boot provider, and that
        this will trigger auto provision of the corresponding fw-utils."""

        subprocess.check_call(
            ["debugfs", "-R", "dump /sbin/fw_setenv fw_setenv.tmp", latest_rootfs]
        )

        try:
            # Fix "UnicodeDecodeError: 'utf-8' codec can't decode byte" error by reading
            # file in the binary format and compare with binary data instead of strings comparision.
            with open("fw_setenv.tmp", "rb") as fd:
                # The vanilla version should not have our custom string.
                assert (
                    b"TestStringThatMustOccur_Mender!#%&" not in fd.read()
                ), "fw_setenv.tmp contains unexpected substring"
        finally:
            os.unlink("fw_setenv.tmp")

        # Get rid of build outputs in deploy directory that may get in the way.
        build_image(
            prepared_test_build["build_dir"],
            prepared_test_build["bitbake_corebase"],
            bitbake_image,
            target="-c clean u-boot",
        )

        try:
            build_image(
                prepared_test_build["build_dir"],
                prepared_test_build["bitbake_corebase"],
                bitbake_image,
                [
                    'PREFERRED_PROVIDER_u-boot = "u-boot-testing"',
                    'PREFERRED_RPROVIDER_u-boot = "u-boot-testing"',
                ],
            )

            new_rootfs = latest_build_artifact(
                request, prepared_test_build["build_dir"], "core-image*.ext[234]"
            )
            subprocess.check_call(
                ["debugfs", "-R", "dump /sbin/fw_setenv fw_setenv.tmp", new_rootfs]
            )

            try:
                with open("fw_setenv.tmp", "rb") as fd:
                    # If we selected u-boot-testing as the U-Boot provider, fw-utils
                    # should have followed and should also contain the special
                    # substring which that version is patched with.
                    assert (
                        b"TestStringThatMustOccur_Mender!#%&" in fd.read()
                    ), "fw_setenv.tmp does not contain expected substring"
            finally:
                os.unlink("fw_setenv.tmp")
        finally:
            # Get rid of build outputs in deploy directory that may get in the
            # way.
            build_image(
                prepared_test_build["build_dir"],
                prepared_test_build["bitbake_corebase"],
                bitbake_image,
                target="-c clean u-boot-testing",
            )

        # Reset local.conf.
        reset_build_conf(prepared_test_build["build_dir"])

        bitbake_vars = get_bitbake_variables(
            request, "u-boot", prepared_test_build=prepared_test_build
        )
        if bitbake_vars["MENDER_UBOOT_AUTO_CONFIGURE"] == "0":
            # The rest of the test is irrelevant if MENDER_UBOOT_AUTO_CONFIGURE
            # is already off.
            return

        try:
            # Capture and discard output, it looks very ugly in the log.
            build_image(
                prepared_test_build["build_dir"],
                prepared_test_build["bitbake_corebase"],
                bitbake_image,
                ['MENDER_UBOOT_AUTO_CONFIGURE_pn-u-boot = "0"'],
                capture=True,
            )

            pytest.fail(
                "Build should not succeed when MENDER_UBOOT_AUTO_CONFIGURE is turned off"
            )
        except subprocess.CalledProcessError:
            pass

    @pytest.mark.min_mender_version("1.0.0")
    def test_save_mender_auto_configured_patch(
        self, request, prepared_test_build, bitbake_image
    ):
        """Test that we can invoke the save_mender_auto_configured_patch task,
        that it produces a patch file, and that this patch file can be used
        instead of MENDER_UBOOT_AUTO_CONFIGURE."""

        bitbake_variables = get_bitbake_variables(
            request, "u-boot", prepared_test_build=prepared_test_build
        )

        # Only run if auto-configuration is on.
        if (
            "MENDER_UBOOT_AUTO_CONFIGURE" in bitbake_variables
            and bitbake_variables["MENDER_UBOOT_AUTO_CONFIGURE"] == "0"
        ):
            pytest.skip(
                "Test is not applicable when MENDER_UBOOT_AUTO_CONFIGURE is off"
            )

        build_image(
            prepared_test_build["build_dir"],
            prepared_test_build["bitbake_corebase"],
            bitbake_image,
            target="-c save_mender_auto_configured_patch u-boot",
        )

        patch_name = os.path.join(
            bitbake_variables["WORKDIR"], "mender_auto_configured.patch"
        )
        with open(patch_name) as fd:
            content = fd.read()
            # Make sure it looks like a patch.
            assert "---" in content
            assert "+++" in content

        # Now check if we can use the patch.
        new_patch_name = "../../meta-mender-core/recipes-bsp/u-boot/patches/mender_auto_configured.patch"
        shutil.copyfile(patch_name, new_patch_name)

        try:
            # We need to add the code using TEST_SRC_URI_APPEND make sure it is
            # absolutely last, otherwise platform specific layers may add
            # patches after us.

            # Normally changes to SRC_URI are picked up automatically, but since
            # we are sneaking it in via the TEST_SRC_URI_APPEND and its
            # associated python snippet, we need to clean the build manually.
            build_image(
                prepared_test_build["build_dir"],
                prepared_test_build["bitbake_corebase"],
                bitbake_image,
                [
                    'MENDER_UBOOT_AUTO_CONFIGURE_pn-u-boot = "0"',
                    'TEST_SRC_URI_APPEND_pn-u-boot = " file://%s"'
                    % os.path.basename(new_patch_name),
                ],
                target="-c clean u-boot",
            )

            build_image(
                prepared_test_build["build_dir"],
                prepared_test_build["bitbake_corebase"],
                bitbake_image,
                target="u-boot",
            )

        finally:
            build_image(
                prepared_test_build["build_dir"],
                prepared_test_build["bitbake_corebase"],
                bitbake_image,
                target="-c clean u-boot",
            )
            os.unlink(new_patch_name)

    # Would be nice to test this with non-UBI, but we don't currently have any
    # non-boolean values inside Kconfig that we can test for. Boolean settings
    # can't be tested because of the limitations listed in
    # do_check_mender_defines.
    @pytest.mark.only_with_distro_feature("mender-ubi")
    @pytest.mark.min_mender_version("1.0.0")
    def test_incorrect_Kconfig_setting(
        self, request, prepared_test_build, bitbake_image
    ):
        """First produce a patch using the auto-patcher, then disable
        auto-patching and apply the patch with a slight modification that makes
        its settings incompatible, and check that this is detected."""

        bitbake_variables = get_bitbake_variables(
            request, "u-boot", prepared_test_build=prepared_test_build
        )

        # Only run if auto-configuration is on.
        if (
            "MENDER_UBOOT_AUTO_CONFIGURE" in bitbake_variables
            and bitbake_variables["MENDER_UBOOT_AUTO_CONFIGURE"] == "0"
        ):
            pytest.skip(
                "Test is not applicable when MENDER_UBOOT_AUTO_CONFIGURE is off"
            )

        build_image(
            prepared_test_build["build_dir"],
            prepared_test_build["bitbake_corebase"],
            bitbake_image,
            target="-c save_mender_auto_configured_patch u-boot",
        )

        try:
            patch_name = os.path.join(
                bitbake_variables["WORKDIR"], "mender_auto_configured.patch"
            )
            new_patch_name = "../../meta-mender-core/recipes-bsp/u-boot/patches/mender_broken_definition.patch"
            with open(patch_name) as patch, open(new_patch_name, "w") as new_patch:
                for line in patch.readlines():
                    if line.startswith("+CONFIG_MTDIDS_DEFAULT="):
                        # Change to a wrong value:
                        new_patch.write(
                            '+CONFIG_MTDIDS_DEFAULT="nand0-wrongvalue=00000000.flash"\n'
                        )
                    else:
                        new_patch.write(line)

            # We need to add the code using TEST_SRC_URI_APPEND make sure it is
            # absolutely last, otherwise platform specific layers may add
            # patches after us.

            # Normally changes to SRC_URI are picked up automatically, but since
            # we are sneaking it in via the TEST_SRC_URI_APPEND and its
            # associated python snippet, we need to clean the build manually.

            build_image(
                prepared_test_build["build_dir"],
                prepared_test_build["bitbake_corebase"],
                bitbake_image,
                [
                    'MENDER_UBOOT_AUTO_CONFIGURE_pn-u-boot = "0"',
                    'TEST_SRC_URI_APPEND_pn-u-boot = " file://%s"'
                    % os.path.basename(new_patch_name),
                ],
                target="-c clean u-boot",
            )

            try:
                build_image(
                    prepared_test_build["build_dir"],
                    prepared_test_build["bitbake_corebase"],
                    bitbake_image,
                    target="-c compile u-boot",
                )

                # Should never get here.
                pytest.fail(
                    "Bitbake succeeded even though we intentionally broke the patch!"
                )

            except subprocess.CalledProcessError as e:
                # A bit risky change after upgrading tests from python2.7 to python3.
                # It seems that underneath subprocess.check_output() call in not
                # capturing the output as `capture_output` flag is not set.
                if e.output:
                    assert e.output.find("Please fix U-Boot's configuration file") >= 0

        finally:
            build_image(
                prepared_test_build["build_dir"],
                prepared_test_build["bitbake_corebase"],
                bitbake_image,
                target="-c clean u-boot",
            )
            os.unlink(new_patch_name)
