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

import os
import pytest
import subprocess
import re
import json

# Make sure common is imported after fabric, because we override some functions.
from common import *

def extract_partition(img, number):
    output = subprocess.Popen(["fdisk", "-l", "-o", "device,start,end", img],
                              stdout=subprocess.PIPE)
    for line in output.stdout:
        if re.search("img%d" % number, line) is None:
            continue

        match = re.match("\s*\S+\s+(\S+)\s+(\S+)", line)
        assert(match is not None)
        start = int(match.group(1))
        end = (int(match.group(2)) + 1)
    output.wait()

    subprocess.check_call(["dd", "if=" + img, "of=img%d.fs" % number,
                           "skip=%d" % start, "count=%d" % (end - start)])

class EmbeddedBootloader:
    loader = None
    offset = 0

    def __init__(self, bitbake_variables, loader_base, offset):
        loader_dir = bitbake_variables['DEPLOY_DIR_IMAGE']
        loader = None

        if loader_base is not None and loader_base != "":
            loader = os.path.join(loader_dir, file)

        self.loader = loader
        self.offset = offset


class TestBuild:
    @pytest.mark.min_mender_version("1.0.0")
    def test_default_server_certificate(self):
        """Test that the md5sum we have on record matches the server certificate.
        This makes sure the warning about this certificate is correct."""

        output = subprocess.check_output(["md5sum", "../../meta-mender-demo/recipes-mender/mender/files/server.crt"])

        # Crude check, just make sure it occurs in the build file.
        subprocess.check_call("fgrep %s ../../meta-mender-core/recipes-mender/mender/mender.inc >/dev/null 2>&1"
                              % output.split()[0], shell=True)


    @pytest.mark.only_with_image('sdimg')
    @pytest.mark.min_mender_version("1.0.0")
    def test_bootloader_embed(self, prepared_test_build):
        """Test that MENDER_IMAGE_BOOTLOADER_FILE causes the bootloader to be embedded
        correctly in the resulting sdimg."""

        loader_file = "bootloader.bin"
        loader_offset = 4
        add_to_local_conf(prepared_test_build, 'MENDER_IMAGE_BOOTLOADER_FILE = "%s"' % loader_file)
        add_to_local_conf(prepared_test_build, 'MENDER_IMAGE_BOOTLOADER_BOOTSECTOR_OFFSET = "%d"' % loader_offset)

        new_bb_vars = get_bitbake_variables("core-image-minimal", prepared_test_build['env_setup'])

        loader_dir = new_bb_vars['DEPLOY_DIR_IMAGE']
        loader_path = os.path.join(loader_dir, loader_file)

        run_verbose("mkdir -p %s" % os.path.dirname(loader_path))
        run_verbose("cp /etc/os-release %s" % loader_path)

        run_bitbake(prepared_test_build)

        built_sdimg = latest_build_artifact(prepared_test_build['build_dir'], "core-image*.sdimg")

        original = os.open(loader_path, os.O_RDONLY)
        embedded = os.open(built_sdimg, os.O_RDONLY)
        os.lseek(embedded, loader_offset * 512, 0)

        checked = 0
        block_size = 4096
        while True:
            org_read = os.read(original, block_size)
            org_read_size = len(org_read)
            emb_read = os.read(embedded, org_read_size)

            assert(org_read == emb_read), "Embedded bootloader is not identical to the file specified in MENDER_IMAGE_BOOTLOADER_FILE"

            if org_read_size < block_size:
                break

        os.close(original)
        os.close(embedded)


    @pytest.mark.only_with_image('ext4', 'ext3', 'ext2')
    @pytest.mark.min_mender_version("1.0.0")
    def test_image_rootfs_extra_space(self, prepared_test_build, bitbake_variables):
        """Test that setting IMAGE_ROOTFS_EXTRA_SPACE to arbitrary values does
        not break the build."""

        add_to_local_conf(prepared_test_build, 'IMAGE_ROOTFS_EXTRA_SPACE_append = " + 640 - 222 + 900"')

        run_bitbake(prepared_test_build)

        built_rootfs = latest_build_artifact(prepared_test_build['build_dir'], "core-image*.ext4")

        assert(os.stat(built_rootfs).st_size == int(bitbake_variables['MENDER_CALC_ROOTFS_SIZE']) * 1024)


    @pytest.mark.only_with_image('ext4', 'ext3', 'ext2')
    @pytest.mark.min_mender_version("1.0.0")
    def test_tenant_token(self, prepared_test_build):
        """Test setting a custom tenant-token"""

        add_to_local_conf(prepared_test_build, 'MENDER_TENANT_TOKEN = "%s"'
                          %  "authtentoken")

        add_to_local_conf(prepared_test_build, 'IMAGE_FSTYPES += "dataimg"')

        run_bitbake(prepared_test_build)

        built_rootfs = latest_build_artifact(prepared_test_build['build_dir'], "core-image*.dataimg")

        subprocess.check_call(["debugfs", "-R",
                                   "dump -p /etc/mender/mender.conf mender.conf", built_rootfs])

        try:
            with open("mender.conf") as fd:
                data = json.load(fd)
            assert data['TenantToken'] == "authtentoken"

        finally:
            os.remove("mender.conf")



    @pytest.mark.only_with_image('ext4', 'ext3', 'ext2')
    @pytest.mark.min_mender_version("1.1.0")
    def test_artifact_signing_keys(self, prepared_test_build, bitbake_variables, bitbake_path):
        """Test that MENDER_ARTIFACT_SIGNING_KEY and MENDER_ARTIFACT_VERIFY_KEY
        works correctly."""

        add_to_local_conf(prepared_test_build, 'MENDER_ARTIFACT_SIGNING_KEY = "%s"'
                          % os.path.join(os.getcwd(), signing_key("RSA").private))
        add_to_local_conf(prepared_test_build, 'MENDER_ARTIFACT_VERIFY_KEY = "%s"'
                          % os.path.join(os.getcwd(), signing_key("RSA").public))

        run_bitbake(prepared_test_build)

        built_rootfs = latest_build_artifact(prepared_test_build['build_dir'], "core-image*.ext[234]")
        # Copy out the key we just added from the image and use that to
        # verify instead of the original, just to be sure.
        subprocess.check_call(["debugfs", "-R",
                               "dump -p /etc/mender/artifact-verify-key.pem artifact-verify-key.pem",
                               built_rootfs])
        try:
            built_artifact = latest_build_artifact(prepared_test_build['build_dir'], "core-image*.mender")
            output = subprocess.check_output(["mender-artifact", "read", "-k",
                                              os.path.join(os.getcwd(), "artifact-verify-key.pem"),
                                              built_artifact])
            assert(output.find("Signature: signed and verified correctly") >= 0)

        finally:
            os.remove("artifact-verify-key.pem")

    @pytest.mark.only_with_image('ext4', 'ext3', 'ext2')
    @pytest.mark.min_mender_version("1.2.0")
    def test_state_scripts(self, prepared_test_build, bitbake_variables, bitbake_path, latest_rootfs, latest_mender_image):
        """Test that state scripts that are specified in the build are included
        correctly."""

        # First verify that the base build does *not* contain any state scripts.
        # Check rootfs.
        output = subprocess.check_output(["debugfs", "-R", "ls -p /etc/mender", latest_rootfs])
        for line in output.split('\n'):
            if len(line) == 0:
                continue

            entry = line.split('/')
            if entry[5] == "scripts":
                # The scripts directory exists. That is fine in itself, but it
                # should not contain any script files ("version" is allowed).
                output = subprocess.check_output(["debugfs", "-R", "ls -p /etc/mender/scripts", latest_rootfs])
                for line in output.split('\n'):
                    if len(line) == 0:
                        continue

                    entry = line.split('/')
                    assert entry[5] == "." or entry[5] == ".." or entry[5] == "version", "There should be no script file in /etc/mender/scripts"
                break

        # Check artifact.
        output = subprocess.check_output("tar xOf %s header.tar.gz| tar tz"
                                         % latest_mender_image, shell=True)
        for line in output.strip().split('\n'):
            if line == "scripts":
                output = subprocess.check_output("tar xOf %s header.tar.gz| tar tz scripts"
                                                 % latest_mender_image, shell=True)
                assert len(output.strip()) == 0, "Unexpected scripts in base image: %s" % output

        try:
            # Alright, now build a new image containing scripts.
            add_to_local_conf(prepared_test_build, 'IMAGE_INSTALL_append = " example-state-scripts"')
            run_bitbake(prepared_test_build)

            found_rootfs_scripts = {
                "version": False,
                "Idle_Enter_00": False,
                "Sync_Enter_10": False,
                "Sync_Leave_90": False,
            }
            found_artifact_scripts = {
                "ArtifactInstall_Enter_00": False,
                "ArtifactInstall_Leave_99": False,
                "ArtifactReboot_Leave_50": False,
                "ArtifactCommit_Enter_50": False,
                "ArtifactCommit_Leave_50": False,
            }

            # Check new rootfs.
            built_rootfs = latest_build_artifact(prepared_test_build['build_dir'], "core-image*.ext[234]")
            output = subprocess.check_output(["debugfs", "-R", "ls -p /etc/mender/scripts", built_rootfs])
            for line in output.split('\n'):
                if len(line) == 0:
                    continue

                entry = line.split('/')

                if entry[5] == "." or entry[5] == "..":
                    continue

                assert found_rootfs_scripts.get(entry[5]) is not None, "Unexpected script in rootfs %s" % entry[5]
                found_rootfs_scripts[entry[5]] = True

            for script in found_rootfs_scripts:
                assert found_rootfs_scripts[script], "%s not found in rootfs script list" % script

            # Check new artifact.
            built_mender_image = latest_build_artifact(prepared_test_build['build_dir'], "core-image*.mender")
            output = subprocess.check_output("tar xOf %s header.tar.gz| tar tz scripts"
                                             % built_mender_image, shell=True)
            for line in output.strip().split('\n'):
                script = os.path.basename(line)
                assert found_artifact_scripts.get(script) is not None, "Unexpected script in image: %s" % script
                found_artifact_scripts[script] = True

            for script in found_artifact_scripts:
                assert found_artifact_scripts[script], "%s not found in artifact script list" % script

        finally:
            # Clean up the state scripts directory. Ideally this wouldn't be
            # necessary, but unfortunately bitbake does not clean up deployment
            # files from recipes that are not included in the current build, so
            # we have to do it manually.
            run_bitbake(prepared_test_build, "-c clean example-state-scripts")

    @pytest.mark.min_mender_version('1.0.0')
    # The extra None elements are to check for no preferred version,
    # e.g. latest.
    @pytest.mark.parametrize(
        "recipe,version",
        [("mender", version) for version in versions_of_recipe("mender")]
        + [("mender", None)]
        + [
            ("mender-artifact-native", version)
            for version in versions_of_recipe("mender-artifact")
        ]
        + [("mender-artifact-native", None)]
        + [
            ("mender-connect", version)
            for version in versions_of_recipe("mender-connect")
        ]
        + [("mender-connect", None)]
        + [
            ("mender-configure", version)
            for version in versions_of_recipe("mender-configure")
        ]
        + [("mender-configure", None)],
    )
    def test_preferred_versions(self, prepared_test_build, recipe, version):
        """Most CI builds build with PREFERRED_VERSION set, because we want to
        build from a specific SHA. This test tests that we can change that or
        turn it off and the build still works."""

        old_file = prepared_test_build['local_conf_orig']
        new_file = prepared_test_build['local_conf']

        if recipe.endswith("-native"):
            base_recipe = recipe[:-len("-native")]
        else:
            base_recipe = recipe

        for pn_style in ["", "pn-"]:
            with open(old_file) as old_fd, open(new_file, "w") as new_fd:
                for line in old_fd.readlines():
                    if re.match('^EXTERNALSRC_pn-%s(-native)? *=' % base_recipe, line) is not None:
                        continue
                    elif re.match("^PREFERRED_VERSION_(pn-)?%s(-native)? *=" % base_recipe, line) is not None:
                        continue
                    else:
                        new_fd.write(line)
                if version is not None:
                    new_fd.write('PREFERRED_VERSION_%s%s = "%s"\n' % (pn_style, base_recipe, version))
                    new_fd.write('PREFERRED_VERSION_%s%s-native = "%s"\n' % (pn_style, base_recipe, version))

            run_verbose("%s && bitbake %s" % (prepared_test_build['env_setup'], recipe))

    @pytest.mark.min_mender_version('1.1.0')
    def test_multiple_device_types_compatible(self, prepared_test_build, bitbake_path, bitbake_variables):
        """Tests that we can include multiple device_types in the artifact."""

        add_to_local_conf(prepared_test_build, 'MENDER_DEVICE_TYPES_COMPATIBLE = "machine1 machine2"')
        run_bitbake(prepared_test_build)

        image = latest_build_artifact(prepared_test_build['build_dir'], 'core-image*.mender')

        output = run_verbose("mender-artifact read %s" % image, capture=True)
        assert "Compatible devices: '[machine1 machine2]'" in output

        output = subprocess.check_output("tar xOf %s header.tar.gz | tar xOz header-info" % image, shell=True)
        data = json.loads(output)
        if version_is_minimum(bitbake_variables, "mender-artifact", "3.0.0"):
            assert data["artifact_depends"]["device_type"] == ["machine1", "machine2"]
        else:
            assert data["device_types_compatible"] == ["machine1", "machine2"]

    @pytest.mark.only_for_machine('vexpress-qemu-flash')
    @pytest.mark.min_mender_version('1.3.0')
    @pytest.mark.parametrize('test_case_name,test_case', [
        ("Default", {
            "vars": [],
            "success": True,
            "expected": {
                "MENDER_MTDIDS": "nor2=40000000.flash",
                "MENDER_IS_ON_MTDID": "40000000.flash",
                "MENDER_MTDPARTS": "40000000.flash:1m(u-boot)ro,-(ubi)",
            },
        }),
        ("custom_mtdids", {
            "vars": [
                'MENDER_MTDIDS = "nor3=40000001.flash"',
            ],
            "success": True,
            "expected": {
                "MENDER_MTDIDS": "nor3=40000001.flash",
                "MENDER_IS_ON_MTDID": "40000001.flash",
                "MENDER_MTDPARTS": "40000001.flash:1m(u-boot)ro,-(ubi)",
            },
        }),
        ("multiple_mtdids_no_selected_one", {
            "vars": [
                'MENDER_MTDIDS = "nor2=40000000.flash,nor3=50000000.flash"',
            ],
            "success": False,
            "expected": {
                "MENDER_MTDIDS": "nor2=40000000.flash,nor3=50000000.flash",
            },
        }),
        ("multiple_mtdids_and_selected_one", {
            "vars": [
                'MENDER_MTDIDS = "nor2=40000001.flash,nor3=50000000.flash"',
                'MENDER_IS_ON_MTDID = "40000001.flash"',
            ],
            "success": False,
            "expected": {
                "MENDER_MTDIDS": "nor2=40000001.flash,nor3=50000000.flash",
                "MENDER_IS_ON_MTDID": "40000001.flash",
            },
        }),
        ("multiple_mtdparts", {
            "vars": [
                'MENDER_MTDIDS = "nor2=40000000.flash,nor3=50000000.flash"',
                'MENDER_IS_ON_MTDID = "40000000.flash"',
                'MENDER_MTDPARTS = "50000000.flash:1m(whatever);40000000.flash:2m(u-boot)ro,3m(u-boot-env),-(ubi)"',
            ],
            "success": True,
            "expected": {
                "MENDER_MTDIDS": "nor2=40000000.flash,nor3=50000000.flash",
                "MENDER_IS_ON_MTDID": "40000000.flash",
                "MENDER_MTDPARTS": "50000000.flash:1m(whatever);40000000.flash:2m(u-boot)ro,3m(u-boot-env),-(ubi)",
            },
        }),
    ])
    def test_various_mtd_combinations(self, test_case_name, test_case, prepared_test_build):
        """Tests that we can build with various combinations of MTD variables,
        and that they receive the correct values."""

        add_to_local_conf(prepared_test_build, "\n".join(test_case["vars"]))
        try:
            run_bitbake(prepared_test_build)
            assert test_case['success'], "Build succeeded, but should fail"
        except subprocess.CalledProcessError:
            assert not test_case['success'], "Build failed"

        variables = get_bitbake_variables(prepared_test_build['image_name'],
                                          prepared_test_build['env_setup'])

        for key in test_case['expected']:
            assert test_case['expected'][key] == variables[key]

    @pytest.mark.only_with_image('sdimg', 'uefiimg')
    @pytest.mark.min_mender_version('1.0.0')
    def test_boot_partition_population(self, prepared_test_build, bitbake_path):
        # Notice in particular a mix of tabs, newlines and spaces. All there to
        # check that whitespace it treated correctly.
        add_to_local_conf(prepared_test_build, """
IMAGE_INSTALL_append = " test-boot-files"

IMAGE_BOOT_FILES_append = " deployed-test1 deployed-test-dir2/deployed-test2 \
	deployed-test3;renamed-deployed-test3 \
 deployed-test-dir4/deployed-test4;renamed-deployed-test4	deployed-test5;renamed-deployed-test-dir5/renamed-deployed-test5 \
deployed-test-dir6/deployed-test6;renamed-deployed-test-dir6/renamed-deployed-test6 \
deployed-test-dir7/* \
deployed-test-dir8/*;./ \
deployed-test-dir9/*;renamed-deployed-test-dir9/ \
"
""")
        run_bitbake(prepared_test_build)

        image = latest_build_artifact(prepared_test_build['build_dir'], "core-image*.*img")
        extract_partition(image, 1)
        try:
            listing = run_verbose("mdir -i img1.fs -b -/", capture=True).split()
            expected = [
                "::/deployed-test1",
                "::/deployed-test2",
                "::/renamed-deployed-test3",
                "::/renamed-deployed-test4",
                "::/renamed-deployed-test-dir5/renamed-deployed-test5",
                "::/renamed-deployed-test-dir6/renamed-deployed-test6",
                "::/deployed-test7",
                "::/deployed-test8",
                "::/renamed-deployed-test-dir9/deployed-test9",
            ]
            assert(all([item in listing for item in expected]))

            # Conflicting file with the same content should pass.
            add_to_local_conf(prepared_test_build, 'IMAGE_BOOT_FILES_append = " conflict-test1"')
            run_bitbake(prepared_test_build)

            # Conflicting file with different content should fail.
            add_to_local_conf(prepared_test_build, 'IMAGE_BOOT_FILES_append = " conflict-test2"')
            try:
                run_bitbake(prepared_test_build)
                pytest.fail("Bitbake succeeded, but should have failed with a file conflict")
            except subprocess.CalledProcessError:
                pass
        finally:
            os.remove("img1.fs")

    @pytest.mark.only_with_image('sdimg', 'uefiimg')
    @pytest.mark.min_mender_version('2.0.0')
    def test_module_install(self, prepared_test_build, bitbake_path, latest_rootfs):
        mender_vars = get_bitbake_variables("mender")
        if "modules" in mender_vars['PACKAGECONFIG'].split():
            originally_on = True
        else:
            originally_on = False

        output = subprocess.check_output(["debugfs", "-R", "ls -p /usr/share/mender", latest_rootfs])
        entries = [elem.split('/')[5] for elem in output.split('\n') if elem.startswith('/')]

        if originally_on:
            assert "modules" in entries
            add_to_local_conf(prepared_test_build, 'PACKAGECONFIG_remove = "modules"')
        else:
            assert "modules" not in entries
            add_to_local_conf(prepared_test_build, 'PACKAGECONFIG_append = " modules"')
        run_bitbake(prepared_test_build)

        new_rootfs = latest_build_artifact(prepared_test_build['build_dir'], "core-image*.ext4")

        output = subprocess.check_output(["debugfs", "-R", "ls -p /usr/share/mender", new_rootfs])
        entries = [elem.split('/')[5] for elem in output.split('\n') if elem.startswith('/')]

        if originally_on:
            assert "modules" not in entries
        else:
            assert "modules" in entries

    @pytest.mark.only_with_image('sdimg', 'uefiimg', 'gptimg', 'biosimg')
    @pytest.mark.min_mender_version('1.0.0')
    def test_correct_partition_types(self, latest_part_image):
        """Test that all the partitions in the image have the correct type."""

        sdimg   = latest_part_image.endswith(".sdimg")
        uefiimg = latest_part_image.endswith(".uefiimg")
        gptimg  = latest_part_image.endswith(".gptimg")
        biosimg = latest_part_image.endswith(".biosimg")

        if sdimg or biosimg:
            # MBR partition table.

            # Example MBR table:
            #
            # Device       Boot  Start     End Sectors  Size Id Type
            # image.sdimg1 *     16384   49151   32768   16M  c W95 FAT
            # image.sdimg2       49152  507903  458752  224M 83 Linux
            # image.sdimg3      507904  966655  458752  224M 83 Linux
            # image.sdimg4      966656 1228799  262144  128M 83 Linux

            output = subprocess.check_output(["fdisk", "-l", latest_part_image])
            lines = output.split('\n')

            # Find the line which starts with "Device".
            table_start = 0
            for line in lines:
                if line.startswith("Device "):
                    break
                table_start += 1
            else:
                assert False, 'No "Device" found in:\n%s' % output
            table_start += 1

            # Let's get rid of the annoying Boot marker which messes up split().
            lines[table_start] = lines[table_start].replace("*", " ")

            expected = [
                ("1", "c"),
                ("2", "83"),
                ("3", "83"),
                ("4", "83"),
            ]

            actual = [(line.split()[0][-1:], line.split()[5]) for line in lines[table_start:] if line != ""]

            assert expected == actual, "Did not expect table:\n%s" % output

        elif uefiimg or gptimg:
            # GPT partition table.

            # Example GPT table.
            #
            # Number  Start (sector)    End (sector)  Size       Code  Name
            #    1           16384           49151   16.0 MiB    EF00  boot
            #    2           49152          507903   224.0 MiB   8300  primary
            #    3          507904          966655   224.0 MiB   8300  primary
            #    4          966656         1228799   128.0 MiB   8300  primary

            output = subprocess.check_output(["sgdisk", "-p", latest_part_image])
            lines = output.split('\n')

            # Find the line which starts with "Number".
            table_start = 0
            for line in lines:
                if line.startswith("Number "):
                    break
                table_start += 1
            else:
                assert False, 'No "Number" found in:\n%s' % output
            table_start += 1

            if uefiimg:
                expected = [
                    ("1", "EF00"),
                    ("2", "8300"),
                    ("3", "8300"),
                    ("4", "8300"),
                ]
            else:
                expected = [
                    ("1", "0700"),
                    ("2", "8300"),
                    ("3", "8300"),
                    ("4", "8300"),
                ]

            actual = [(line.split()[0], line.split()[5]) for line in lines[table_start:] if line != ""]

            assert expected == actual, "Did not expect table:\n%s" % output

        else:
            assert False, "Should not get here!"
