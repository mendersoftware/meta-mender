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
import subprocess
import re
import json

import pytest

from utils.common import (
    build_image,
    latest_build_artifact,
    get_bitbake_variables,
    run_verbose,
    signing_key,
    versions_of_recipe,
    get_local_conf_path,
    get_local_conf_orig_path,
    make_tempdir,
    version_is_minimum,
    reset_build_conf,
)


def extract_partition(img, number):
    output = subprocess.Popen(
        ["fdisk", "-l", "-o", "device,start,end", img], stdout=subprocess.PIPE
    )
    for line in output.stdout:
        if re.search("img%d" % number, line.decode()) is None:
            continue

        match = re.match(r"\s*\S+\s+(\S+)\s+(\S+)", line.decode())
        assert match is not None
        start = int(match.group(1))
        end = int(match.group(2)) + 1
    output.wait()

    subprocess.check_call(
        [
            "dd",
            "if=" + img,
            "of=img%d.fs" % number,
            "skip=%d" % start,
            "count=%d" % (end - start),
        ]
    )


class TestBuild:
    @pytest.mark.min_mender_version("1.0.0")
    def test_default_server_certificate(self):
        """Test that the md5sum we have on record matches the server certificate.
        This makes sure the warning about this certificate is correct."""

        output = subprocess.check_output(
            [
                "md5sum",
                "../../meta-mender-demo/recipes-mender/mender-client/files/server.crt",
            ]
        )

        # Crude check, just make sure it occurs in the build file.
        subprocess.check_call(
            "fgrep %s ../../meta-mender-core/recipes-mender/mender-client/mender-client.inc >/dev/null 2>&1"
            % output.decode().split()[0],
            shell=True,
        )

    @pytest.mark.min_mender_version("2.5.0")
    def test_certificate_split(self, request, bitbake_image):
        """Test that the certificate added in the mender-server-certificate
        recipe is split correctly."""

        # Currently this is hardcoded to the md5 sums of the split demo
        # certificate as of 2021-04-07. Please update if it is replaced.
        md5sums = """02d20627f63664f9495cea2e54b28e1b  ./usr/local/share/ca-certificates/mender/server-1.crt
b524b8b3f13902ef8014c0af7aa408bc  ./usr/local/share/ca-certificates/mender/server-2.crt"""

        rootfs = get_bitbake_variables(request, bitbake_image)["IMAGE_ROOTFS"]
        output = (
            subprocess.check_output(
                "md5sum ./usr/local/share/ca-certificates/mender/*",
                shell=True,
                cwd=rootfs,
            )
            .decode()
            .strip()
        )

        assert md5sums == output

    @pytest.mark.only_with_image("sdimg")
    @pytest.mark.min_mender_version("1.0.0")
    def test_bootloader_embed(self, request, prepared_test_build, bitbake_image):
        """Test that MENDER_IMAGE_BOOTLOADER_FILE causes the bootloader to be embedded
        correctly in the resulting sdimg."""

        loader_file = "bootloader.bin"
        loader_offset = 4

        new_bb_vars = get_bitbake_variables(
            request, "core-image-minimal", prepared_test_build=prepared_test_build
        )

        loader_dir = new_bb_vars["DEPLOY_DIR_IMAGE"]
        loader_path = os.path.join(loader_dir, loader_file)

        run_verbose("mkdir -p %s" % os.path.dirname(loader_path))
        run_verbose("cp /etc/os-release %s" % loader_path)

        build_image(
            prepared_test_build["build_dir"],
            prepared_test_build["bitbake_corebase"],
            bitbake_image,
            [
                'MENDER_IMAGE_BOOTLOADER_FILE = "%s"' % loader_file,
                'MENDER_IMAGE_BOOTLOADER_BOOTSECTOR_OFFSET = "%d"' % loader_offset,
            ],
        )

        built_sdimg = latest_build_artifact(
            request, prepared_test_build["build_dir"], "core-image*.sdimg"
        )

        original = os.open(loader_path, os.O_RDONLY)
        embedded = os.open(built_sdimg, os.O_RDONLY)
        os.lseek(embedded, loader_offset * 512, 0)

        checked = 0
        block_size = 4096
        while True:
            org_read = os.read(original, block_size)
            org_read_size = len(org_read)
            emb_read = os.read(embedded, org_read_size)

            assert (
                org_read == emb_read
            ), "Embedded bootloader is not identical to the file specified in MENDER_IMAGE_BOOTLOADER_FILE"

            if org_read_size < block_size:
                break

        os.close(original)
        os.close(embedded)

    @pytest.mark.only_with_image("ext4", "ext3", "ext2")
    @pytest.mark.min_mender_version("1.0.0")
    def test_image_rootfs_extra_space(
        self, request, prepared_test_build, bitbake_variables, bitbake_image
    ):
        """Test that setting IMAGE_ROOTFS_EXTRA_SPACE to arbitrary values does
        not break the build."""

        build_image(
            prepared_test_build["build_dir"],
            prepared_test_build["bitbake_corebase"],
            bitbake_image,
            ['IMAGE_ROOTFS_EXTRA_SPACE_append = " + 640 - 222 + 900"'],
        )

        built_rootfs = latest_build_artifact(
            request, prepared_test_build["build_dir"], "core-image*.ext4"
        )

        assert (
            os.stat(built_rootfs).st_size
            == int(bitbake_variables["MENDER_CALC_ROOTFS_SIZE"]) * 1024
        )

    @pytest.mark.only_with_image("ext4", "ext3", "ext2")
    @pytest.mark.min_mender_version("1.0.0")
    def test_tenant_token(self, request, prepared_test_build, bitbake_image):
        """Test setting a custom tenant-token"""

        build_image(
            prepared_test_build["build_dir"],
            prepared_test_build["bitbake_corebase"],
            bitbake_image,
            [
                'MENDER_TENANT_TOKEN = "%s"' % "authtentoken",
                'IMAGE_FSTYPES += "dataimg"',
            ],
        )

        built_rootfs = latest_build_artifact(
            request, prepared_test_build["build_dir"], "core-image*.dataimg"
        )

        subprocess.check_call(
            [
                "debugfs",
                "-R",
                "dump -p /etc/mender/mender.conf mender.conf",
                built_rootfs,
            ]
        )

        try:
            with open("mender.conf") as fd:
                data = json.load(fd)
            assert data["TenantToken"] == "authtentoken"

        finally:
            os.remove("mender.conf")

    @pytest.mark.only_with_image("ext4", "ext3", "ext2")
    @pytest.mark.min_mender_version("1.1.0")
    def test_artifact_signing_keys(
        self,
        request,
        prepared_test_build,
        bitbake_variables,
        bitbake_path,
        bitbake_image,
    ):
        """Test that MENDER_ARTIFACT_SIGNING_KEY and MENDER_ARTIFACT_VERIFY_KEY
        works correctly."""

        build_image(
            prepared_test_build["build_dir"],
            prepared_test_build["bitbake_corebase"],
            bitbake_image,
            [
                'MENDER_ARTIFACT_SIGNING_KEY = "%s"'
                % os.path.join(os.getcwd(), signing_key("RSA").private),
                'MENDER_ARTIFACT_VERIFY_KEY = "%s"'
                % os.path.join(os.getcwd(), signing_key("RSA").public),
            ],
        )

        built_rootfs = latest_build_artifact(
            request, prepared_test_build["build_dir"], "core-image*.ext[234]"
        )
        # Copy out the key we just added from the image and use that to
        # verify instead of the original, just to be sure.
        subprocess.check_call(
            [
                "debugfs",
                "-R",
                "dump -p /etc/mender/artifact-verify-key.pem artifact-verify-key.pem",
                built_rootfs,
            ]
        )
        try:
            built_artifact = latest_build_artifact(
                request, prepared_test_build["build_dir"], "core-image*.mender"
            )
            output = subprocess.check_output(
                [
                    "mender-artifact",
                    "read",
                    "-k",
                    os.path.join(os.getcwd(), "artifact-verify-key.pem"),
                    built_artifact,
                ]
            ).decode()
            assert output.find("Signature: signed and verified correctly") >= 0

        finally:
            os.remove("artifact-verify-key.pem")

    @pytest.mark.only_with_image("ext4", "ext3", "ext2")
    @pytest.mark.min_mender_version("1.2.0")
    def test_state_scripts(
        self,
        request,
        prepared_test_build,
        bitbake_variables,
        bitbake_path,
        latest_rootfs,
        latest_mender_image,
        bitbake_image,
    ):
        """Test that state scripts that are specified in the build are included
        correctly."""

        # First verify that the base build does *not* contain any state scripts.
        # Check rootfs.
        output = subprocess.check_output(
            ["debugfs", "-R", "ls -p /etc/mender", latest_rootfs]
        ).decode()
        for line in output.split("\n"):
            if len(line) == 0:
                continue

            entry = line.split("/")
            if entry[5] == "scripts":
                # The scripts directory exists. That is fine in itself, but it
                # should not contain any script files ("version" is allowed).
                output = subprocess.check_output(
                    ["debugfs", "-R", "ls -p /etc/mender/scripts", latest_rootfs]
                ).decode()
                for line in output.split("\n"):
                    if len(line) == 0:
                        continue

                    entry = line.split("/")
                    assert (
                        entry[5] == "." or entry[5] == ".." or entry[5] == "version"
                    ), "There should be no script file in /etc/mender/scripts"
                break

        # Check artifact.
        output = subprocess.check_output(
            "tar xOf %s header.tar.gz| tar tz" % latest_mender_image, shell=True
        ).decode()
        for line in output.strip().split("\n"):
            if line == "scripts":
                output = subprocess.check_output(
                    "tar xOf %s header.tar.gz| tar tz scripts" % latest_mender_image,
                    shell=True,
                ).decode()
                assert len(output.strip()) == 0, (
                    "Unexpected scripts in base image: %s" % output
                )

        try:
            # Alright, now build a new image containing scripts.
            build_image(
                prepared_test_build["build_dir"],
                prepared_test_build["bitbake_corebase"],
                bitbake_image,
                ['IMAGE_INSTALL_append = " example-state-scripts"'],
            )

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
            built_rootfs = latest_build_artifact(
                request, prepared_test_build["build_dir"], "core-image*.ext[234]"
            )
            output = subprocess.check_output(
                ["debugfs", "-R", "ls -p /etc/mender/scripts", built_rootfs]
            ).decode()
            for line in output.split("\n"):
                if len(line) == 0:
                    continue

                entry = line.split("/")

                if entry[5] == "." or entry[5] == "..":
                    continue

                assert found_rootfs_scripts.get(entry[5]) is not None, (
                    "Unexpected script in rootfs %s" % entry[5]
                )
                found_rootfs_scripts[entry[5]] = True

            for script in found_rootfs_scripts:
                assert found_rootfs_scripts[script], (
                    "%s not found in rootfs script list" % script
                )

            # Check new artifact.
            built_mender_image = latest_build_artifact(
                request, prepared_test_build["build_dir"], "core-image*.mender"
            )
            output = subprocess.check_output(
                "tar xOf %s header.tar.gz| tar tz scripts" % built_mender_image,
                shell=True,
            ).decode()
            for line in output.strip().split("\n"):
                script = os.path.basename(line)
                assert found_artifact_scripts.get(script) is not None, (
                    "Unexpected script in image: %s" % script
                )
                found_artifact_scripts[script] = True

            for script in found_artifact_scripts:
                assert found_artifact_scripts[script], (
                    "%s not found in artifact script list" % script
                )

        finally:
            # Clean up the state scripts directory. Ideally this wouldn't be
            # necessary, but unfortunately bitbake does not clean up deployment
            # files from recipes that are not included in the current build, so
            # we have to do it manually.
            build_image(
                prepared_test_build["build_dir"],
                prepared_test_build["bitbake_corebase"],
                bitbake_image,
                target="-c clean example-state-scripts",
            )

    @pytest.mark.min_mender_version("1.0.0")
    # The extra None elements are to check for no preferred version,
    # e.g. latest.
    @pytest.mark.parametrize(
        "recipe,version",
        [("mender-client", version) for version in versions_of_recipe("mender-client")]
        + [("mender-client", None)]
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

        old_file = get_local_conf_orig_path(prepared_test_build["build_dir"])
        new_file = get_local_conf_path(prepared_test_build["build_dir"])

        if recipe.endswith("-native"):
            base_recipe = recipe[: -len("-native")]
        else:
            base_recipe = recipe

        for pn_style in ["", "pn-"]:
            with open(old_file) as old_fd, open(new_file, "w") as new_fd:
                for line in old_fd.readlines():
                    if (
                        re.match("^EXTERNALSRC_pn-%s(-native)? *=" % base_recipe, line)
                        is not None
                    ):
                        continue
                    elif (
                        re.match(
                            "^PREFERRED_VERSION_(pn-)?%s(-native)? *=" % base_recipe,
                            line,
                        )
                        is not None
                    ):
                        continue
                    else:
                        new_fd.write(line)
                if version is not None:
                    new_fd.write(
                        'PREFERRED_VERSION_%s%s = "%s"\n'
                        % (pn_style, base_recipe, version)
                    )
                    new_fd.write(
                        'PREFERRED_VERSION_%s%s-native = "%s"\n'
                        % (pn_style, base_recipe, version)
                    )

            init_env_cmd = "cd %s && . oe-init-build-env %s" % (
                prepared_test_build["bitbake_corebase"],
                prepared_test_build["build_dir"],
            )
            run_verbose("%s && bitbake %s" % (init_env_cmd, recipe))

    @pytest.mark.min_mender_version("1.1.0")
    def test_multiple_device_types_compatible(
        self,
        request,
        prepared_test_build,
        bitbake_path,
        bitbake_variables,
        bitbake_image,
    ):
        """Tests that we can include multiple device_types in the artifact."""

        build_image(
            prepared_test_build["build_dir"],
            prepared_test_build["bitbake_corebase"],
            bitbake_image,
            ['MENDER_DEVICE_TYPES_COMPATIBLE = "machine1 machine2"'],
        )

        image = latest_build_artifact(
            request, prepared_test_build["build_dir"], "core-image*.mender"
        )

        output = run_verbose("mender-artifact read %s" % image, capture=True)
        assert b"Compatible devices: '[machine1 machine2]'" in output

        output = subprocess.check_output(
            "tar xOf %s header.tar.gz | tar xOz header-info" % image, shell=True
        ).decode()
        data = json.loads(output)
        if version_is_minimum(bitbake_variables, "mender-artifact", "3.0.0"):
            assert data["artifact_depends"]["device_type"] == ["machine1", "machine2"]
        else:
            assert data["device_types_compatible"] == ["machine1", "machine2"]

    @pytest.mark.only_for_machine("vexpress-qemu-flash")
    @pytest.mark.min_mender_version("1.3.0")
    @pytest.mark.parametrize(
        "test_case_name,test_case",
        [
            (
                "Default",
                {
                    "vars": [],
                    "success": True,
                    "expected": {
                        "MENDER_MTDIDS": "nor2=40000000.flash",
                        "MENDER_IS_ON_MTDID": "40000000.flash",
                        "MENDER_MTDPARTS": "40000000.flash:1m(u-boot)ro,-(ubi)",
                    },
                },
            ),
            (
                "custom_mtdids",
                {
                    "vars": ['MENDER_MTDIDS = "nor3=40000001.flash"'],
                    "success": True,
                    "expected": {
                        "MENDER_MTDIDS": "nor3=40000001.flash",
                        "MENDER_IS_ON_MTDID": "40000001.flash",
                        "MENDER_MTDPARTS": "40000001.flash:1m(u-boot)ro,-(ubi)",
                    },
                },
            ),
            (
                "multiple_mtdids_no_selected_one",
                {
                    "vars": [
                        'MENDER_MTDIDS = "nor2=40000000.flash,nor3=50000000.flash"'
                    ],
                    "success": False,
                    "expected": {
                        "MENDER_MTDIDS": "nor2=40000000.flash,nor3=50000000.flash"
                    },
                },
            ),
            (
                "multiple_mtdids_and_selected_one",
                {
                    "vars": [
                        'MENDER_MTDIDS = "nor2=40000001.flash,nor3=50000000.flash"',
                        'MENDER_IS_ON_MTDID = "40000001.flash"',
                    ],
                    "success": False,
                    "expected": {
                        "MENDER_MTDIDS": "nor2=40000001.flash,nor3=50000000.flash",
                        "MENDER_IS_ON_MTDID": "40000001.flash",
                    },
                },
            ),
            (
                "multiple_mtdparts",
                {
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
                },
            ),
        ],
    )
    def test_various_mtd_combinations(
        self, request, test_case_name, test_case, prepared_test_build, bitbake_image
    ):
        """Tests that we can build with various combinations of MTD variables,
        and that they receive the correct values."""

        try:
            build_image(
                prepared_test_build["build_dir"],
                prepared_test_build["bitbake_corebase"],
                bitbake_image,
                ["\n".join(test_case["vars"])],
            )
            assert test_case["success"], "Build succeeded, but should fail"
        except subprocess.CalledProcessError:
            assert not test_case["success"], "Build failed"

        variables = get_bitbake_variables(
            request, bitbake_image, prepared_test_build=prepared_test_build
        )

        for key in test_case["expected"]:
            assert test_case["expected"][key] == variables[key]

    @pytest.mark.only_with_image("sdimg", "uefiimg")
    @pytest.mark.min_mender_version("1.0.0")
    def test_boot_partition_population(
        self, request, prepared_test_build, bitbake_path, bitbake_image
    ):
        # Notice in particular a mix of tabs, newlines and spaces. All there to
        # check that whitespace it treated correctly.

        build_image(
            prepared_test_build["build_dir"],
            prepared_test_build["bitbake_corebase"],
            bitbake_image,
            [
                """
IMAGE_INSTALL_append = " test-boot-files"

IMAGE_BOOT_FILES_append = " deployed-test1 deployed-test-dir2/deployed-test2 \
    deployed-test3;renamed-deployed-test3 \
 deployed-test-dir4/deployed-test4;renamed-deployed-test4	deployed-test5;renamed-deployed-test-dir5/renamed-deployed-test5 \
deployed-test-dir6/deployed-test6;renamed-deployed-test-dir6/renamed-deployed-test6 \
deployed-test-dir7/* \
deployed-test-dir8/*;./ \
deployed-test-dir9/*;renamed-deployed-test-dir9/ \
"
"""
            ],
        )

        image = latest_build_artifact(
            request, prepared_test_build["build_dir"], "core-image*.*img"
        )
        extract_partition(image, 1)
        try:
            listing = (
                run_verbose("mdir -i img1.fs -b -/", capture=True).decode().split()
            )
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
            assert all([item in listing for item in expected])

            # Conflicting file with the same content should pass.
            build_image(
                prepared_test_build["build_dir"],
                prepared_test_build["bitbake_corebase"],
                bitbake_image,
                ['IMAGE_BOOT_FILES_append = " conflict-test1"'],
            )

            # Conflicting file with different content should fail.
            try:
                build_image(
                    prepared_test_build["build_dir"],
                    prepared_test_build["bitbake_corebase"],
                    bitbake_image,
                    ['IMAGE_BOOT_FILES_append = " conflict-test2"'],
                )
                pytest.fail(
                    "Bitbake succeeded, but should have failed with a file conflict"
                )
            except subprocess.CalledProcessError:
                pass
        finally:
            os.remove("img1.fs")

    @pytest.mark.only_with_image("sdimg", "uefiimg")
    @pytest.mark.min_mender_version("2.0.0")
    def test_module_install(
        self, request, prepared_test_build, bitbake_path, latest_rootfs, bitbake_image
    ):
        # List of expected update modules
        default_update_modules = [
            "deb",
            "directory",
            "docker",
            "rootfs-image-v2",
            "rpm",
            "script",
            "single-file",
        ]

        mender_vars = get_bitbake_variables(request, "mender-client")
        if "modules" in mender_vars["PACKAGECONFIG"].split():
            originally_on = True
        else:
            originally_on = False

        output = subprocess.check_output(
            ["debugfs", "-R", "ls -p /usr/share/mender/modules/v3", latest_rootfs]
        ).decode()
        entries = [
            elem.split("/")[5] for elem in output.split("\n") if elem.startswith("/")
        ]

        if originally_on:
            assert all([e in entries for e in default_update_modules])
            build_image(
                prepared_test_build["build_dir"],
                prepared_test_build["bitbake_corebase"],
                bitbake_image,
                ['PACKAGECONFIG_remove = "modules"'],
            )
        else:
            assert not any([e in entries for e in default_update_modules])
            build_image(
                prepared_test_build["build_dir"],
                prepared_test_build["bitbake_corebase"],
                bitbake_image,
                ['PACKAGECONFIG_append = " modules"'],
            )

        new_rootfs = latest_build_artifact(
            request, prepared_test_build["build_dir"], "core-image*.ext4"
        )

        output = subprocess.check_output(
            ["debugfs", "-R", "ls -p /usr/share/mender/modules/v3", new_rootfs]
        ).decode()
        entries = [
            elem.split("/")[5] for elem in output.split("\n") if elem.startswith("/")
        ]

        if originally_on:
            assert not any([e in entries for e in default_update_modules])
        else:
            assert all([e in entries for e in default_update_modules])

    @pytest.mark.only_with_image("sdimg", "uefiimg", "gptimg", "biosimg")
    @pytest.mark.min_mender_version("1.0.0")
    def test_correct_partition_types(self, latest_part_image):
        """Test that all the partitions in the image have the correct type."""

        sdimg = latest_part_image.endswith(".sdimg")
        uefiimg = latest_part_image.endswith(".uefiimg")
        gptimg = latest_part_image.endswith(".gptimg")
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

            output = subprocess.check_output(
                ["fdisk", "-l", latest_part_image]
            ).decode()
            lines = output.split("\n")

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

            expected = [("1", "c"), ("2", "83"), ("3", "83"), ("4", "83")]

            actual = [
                (line.split()[0][-1:], line.split()[5])
                for line in lines[table_start:]
                if line != ""
            ]

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

            output = subprocess.check_output(
                ["sgdisk", "-p", latest_part_image]
            ).decode()
            lines = output.split("\n")

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
                expected = [("1", "EF00"), ("2", "8300"), ("3", "8300"), ("4", "8300")]
            else:
                expected = [("1", "0700"), ("2", "8300"), ("3", "8300"), ("4", "8300")]

            actual = [
                (line.split()[0], line.split()[5])
                for line in lines[table_start:]
                if line != ""
            ]

            assert expected == actual, "Did not expect table:\n%s" % output

        else:
            assert False, "Should not get here!"

    class BuildDependsProvides(object):
        """
        BuildDependsProvides is a utility class for handling the depends and
        provides parameters of a Mender Artifact build
        """

        def __init__(
            self,
            name_depends=[],
            depends={},
            provides={},
            depends_groups=[],
            provides_group="",
        ):
            self.name_depends = name_depends
            self.provides = provides
            self.provides_group = provides_group
            self.depends = depends
            self.depends_groups = depends_groups

        def _flatten_dict(self, d):
            l = ""
            for pair in d.items():
                l += ":".join(pair)
                l += " "
            return l

        def __str__(self):
            s = ""
            if self.name_depends:
                s += 'MENDER_ARTIFACT_NAME_DEPENDS = "{}"\n'.format(
                    " ".join(self.name_depends)
                )

            if self.provides:
                l = self._flatten_dict(self.provides)
                s += 'MENDER_ARTIFACT_PROVIDES = "{}"\n'.format(l)

            if self.provides_group:
                s += 'MENDER_ARTIFACT_PROVIDES_GROUP = "{}"\n'.format(
                    self.provides_group
                )

            if self.depends:
                l = self._flatten_dict(self.depends)
                s += 'MENDER_ARTIFACT_DEPENDS = "{}"\n'.format(l)

            if self.depends_groups:
                s += 'MENDER_ARTIFACT_DEPENDS_GROUPS = "{}"\n'.format(
                    " ".join(self.depends_groups)
                )

            return s

        @staticmethod
        def parse(output):
            """
            Parses the output from Mender Artifact read
            into a BuildDependsProvides instance
            """
            d = TestBuild.BuildDependsProvides()
            lines = output.split("\n")
            for i in range(len(lines)):
                line = lines[i]

                if "Provides group:" in line:
                    s = line[line.index(":") + 1 :].strip()
                    if s is not "":
                        d.provides_group = s

                if "Depends on one of artifact" in line:
                    if "[]" not in line:
                        dps = line[line.index("[") + 1 : line.index("]")].split()
                        dps = [word.replace(",", "") for word in dps]
                        if dps:
                            d.name_depends = dps

                if "Depends on one of group(s)" in line:
                    if "[]" not in line:
                        depends_groups = line[
                            line.index("[") + 1 : line.index("]")
                        ].split()
                        depends_groups = [
                            word.replace(",", "") for word in depends_groups
                        ]
                        if depends_groups:
                            d.depends_groups = depends_groups

                # Precede with two spaces to avoid matching "Clears Provides:".
                if "  Provides:" in line:
                    k = i + 1
                    tmp = {}
                    # Parse all provides on the following lines
                    while True:
                        if "Depends:" in lines[k]:
                            break
                        l = [s.strip() for s in lines[k].split(": ")]
                        assert len(l) == 2, "Line should only contain a key value pair"
                        key, val = l[0], l[1]
                        tmp[key] = val
                        k += 1
                    d.provides = tmp

                if "Depends:" in line:
                    k = i + 1
                    tmp = {}
                    # Parse all depends on the following lines
                    while True:
                        if "Metadata:" in lines[k] or "Clears Provides:" in lines[k]:
                            break
                        l = [s.strip() for s in lines[k].split(": ")]
                        assert len(l) == 2, "Line should only contain a key value pair"
                        key, val = l[0], l[1]
                        tmp[key] = val
                        k += 1
                    d.depends = tmp

            return d

    test_cases = [
        BuildDependsProvides(name_depends=["dependsname1"]),
        BuildDependsProvides(
            name_depends=["dependsname1"],
            provides={"artifactprovidesname": "artifactprovidesvalue"},
        ),
        BuildDependsProvides(
            name_depends=["dependsname1"],
            provides={"artifactprovidesname": "artifactprovidesvalue"},
            provides_group="providesgroupname",
        ),
        BuildDependsProvides(
            name_depends=["dependsname1"],
            provides={"artifactprovidesname": "artifactprovidesvalue"},
            provides_group="providesgroupname",
            depends={"dependskey1": "dependsval1", "dependskey2": "dependsval2"},
        ),
        BuildDependsProvides(
            name_depends=["dependsname0", "dependsname2"],
            provides={"artifactprovidesname": "artifactprovidesvalue"},
            provides_group="providesgroupname",
            depends={"dependskey1": "dependsval1", "dependskey2": "dependsval2"},
            depends_groups=["depenceygroup1", "depenceygroup2"],
        ),
    ]

    @pytest.mark.min_mender_version("2.3.0")
    @pytest.mark.parametrize("dependsprovides", test_cases)
    def test_build_artifact_depends_and_provides(
        self, request, prepared_test_build, bitbake_image, bitbake_path, dependsprovides
    ):
        """Test whether a build with enabled Artifact Provides and Depends does
        indeed add the parameters to the built Artifact"""

        build_image(
            prepared_test_build["build_dir"],
            prepared_test_build["bitbake_corebase"],
            bitbake_image,
            [param for param in str(dependsprovides).splitlines()],
        )

        image = latest_build_artifact(
            request, prepared_test_build["build_dir"], "core-image*.mender"
        )

        output = run_verbose("mender-artifact read %s" % image, capture=True).decode()
        other = TestBuild.BuildDependsProvides.parse(output)

        # MEN-2956: Mender-Artifact now writes rootfs-image-checksum by default.
        # MEN-3482: The new key for the rootfs image checksum is rootfs-image.checksum
        assert (
            "rootfs-image.checksum" in other.provides
            or "rootfs_image_checksum" in other.provides
        ), "Empty rootfs_image_checksum in the built rootfs-image artifact, this should be added by default by `mender-artifact write rootfs-image`"
        # Then remove it, not to mess up the expected test output
        if "rootfs-image.checksum" in other.provides.keys():
            del other.provides["rootfs-image.checksum"]
        if "rootfs_image_checksum" in other.provides.keys():
            del other.provides["rootfs_image_checksum"]

        # MEN-3076: Mender-Artifacts writes software version by default
        # older versions did not, thus we remove the key before asserting the content
        if "rootfs-image.version" in other.provides.keys():
            del other.provides["rootfs-image.version"]

        assert dependsprovides.__dict__ == other.__dict__

    @pytest.mark.only_with_image("sdimg", "uefiimg", "gptimg", "biosimg")
    @pytest.mark.min_mender_version("1.0.0")
    def test_extra_parts(
        self, request, latest_part_image, prepared_test_build, bitbake_image
    ):
        sdimg = latest_part_image.endswith(".sdimg")
        uefiimg = latest_part_image.endswith(".uefiimg")
        gptimg = latest_part_image.endswith(".gptimg")
        biosimg = latest_part_image.endswith(".biosimg")

        with make_tempdir() as tmpdir1, make_tempdir() as tmpdir2, make_tempdir() as tmpdir3, make_tempdir() as tmpdir4:
            with open(os.path.join(tmpdir1, "tmpfile1"), "w") as fd:
                fd.write("Test content1\n")
            with open(os.path.join(tmpdir2, "tmpfile2"), "w") as fd:
                fd.write("Test content2\n")
            with open(os.path.join(tmpdir3, "tmpfile3"), "w") as fd:
                fd.write("Test content3\n")
            with open(os.path.join(tmpdir4, "tmpfile4"), "w") as fd:
                fd.write("Test content4\n")

            build_image(
                prepared_test_build["build_dir"],
                prepared_test_build["bitbake_corebase"],
                bitbake_image,
                [
                    'MENDER_EXTRA_PARTS = "test1 test2 test3 test4"',
                    'MENDER_EXTRA_PARTS[test1] = "--fixed-size 100M --label=test1 --fstype=ext4 --source rootfs --rootfs-dir %s"'
                    % tmpdir1,
                    'MENDER_EXTRA_PARTS[test2] = "--fixed-size 50M --fstype=ext4 --source rootfs --rootfs-dir %s --label=test2"'
                    % tmpdir2,
                    'MENDER_EXTRA_PARTS[test3] = "--fixed-size 50M --fstype=ext4 --source rootfs --rootfs-dir %s --label=test3"'
                    % tmpdir3,
                    'MENDER_EXTRA_PARTS[test4] = "--fixed-size 50M --fstype=ext4 --source rootfs --rootfs-dir %s --label=test4"'
                    % tmpdir4,
                    'MENDER_EXTRA_PARTS_FSTAB[test1] = "auto nouser"',
                    'MENDER_EXTRA_PARTS_FSTAB[test2] = "ext4 default,ro"',
                    'MENDER_EXTRA_PARTS_FSTAB[test3] = "ext4 default,ro 1"',
                    'MENDER_EXTRA_PARTS_FSTAB[test4] = "ext4 default,ro 1 0"',
                ],
            )

        image = latest_build_artifact(request, prepared_test_build["build_dir"], "*img")

        # Take extended partition into account for MBR partition tables.
        if uefiimg or gptimg:
            # Example
            # 1           16384           49151   16.0 MiB    0700  Microsoft basic data
            # 2           49152          507903   224.0 MiB   8300  Linux filesystem
            # 3          507904          966655   224.0 MiB   8300  Linux filesystem
            # 4          983040         1245183   128.0 MiB   8300  Linux filesystem
            # 5         1261568         1466367   100.0 MiB   8300  Linux filesystem
            # 6         1474560         1679359   100.0 MiB   8300  Linux filesystem
            output = subprocess.check_output(["sgdisk", "-p", image]).decode()
            test1_re = r"^\s*5\s+([0-9]+)\s+([0-9]+)\s+100.0\s+MiB\s+8300\s+"
            test2_re = r"^\s*6\s+([0-9]+)\s+([0-9]+)\s+50.0\s+MiB\s+8300\s+"
            test3_re = r"^\s*7\s+([0-9]+)\s+([0-9]+)\s+50.0\s+MiB\s+8300\s+"
            test4_re = r"^\s*8\s+([0-9]+)\s+([0-9]+)\s+50.0\s+MiB\s+8300\s+"
            extra_start = 5
        else:
            # Example:
            # ...sdimg1 *      16384   49151   32768   16M  c W95 FAT32 (LBA)
            # ...sdimg2        49152  507903  458752  224M 83 Linux
            # ...sdimg3       507904  966655  458752  224M 83 Linux
            # ...sdimg4       983039 1576959  593921  290M  f W95 Ext'd (LBA)
            # ...sdimg5       983040 1245183  262144  128M 83 Linux
            # ...sdimg6      1261568 1466367  204800  100M 83 Linux
            # ...sdimg7      1474560 1576959  102400   50M 83 Linux
            output = subprocess.check_output(["fdisk", "-l", image]).decode()
            test1_re = r"img6(?:\s|\*)+([0-9]+)\s+([0-9]+)\s+[0-9]+\s+100M\s+83\s+"
            test2_re = r"img7(?:\s|\*)+([0-9]+)\s+([0-9]+)\s+[0-9]+\s+50M\s+83\s+"
            test3_re = r"img8(?:\s|\*)+([0-9]+)\s+([0-9]+)\s+[0-9]+\s+50M\s+83\s+"
            test4_re = r"img9(?:\s|\*)+([0-9]+)\s+([0-9]+)\s+[0-9]+\s+50M\s+83\s+"
            extra_start = 6

        match1 = re.search(test1_re, output, flags=re.MULTILINE)
        match2 = re.search(test2_re, output, flags=re.MULTILINE)
        match3 = re.search(test3_re, output, flags=re.MULTILINE)
        match4 = re.search(test4_re, output, flags=re.MULTILINE)
        assert match1 is not None
        assert match2 is not None
        assert match3 is not None
        assert match4 is not None

        ext4 = latest_build_artifact(
            request, prepared_test_build["build_dir"], "*.ext4"
        )
        fstab = subprocess.check_output(
            ["debugfs", "-R", "cat /etc/fstab", ext4]
        ).decode()

        # Example:
        # /dev/mmcblk0p5       /mnt/test1           auto       nouser                0  2
        # /dev/mmcblk0p6       /mnt/test2           auto       default,ro            0  2
        # /dev/mmcblk0p7       /mnt/test3           auto       default,ro            1  2
        # /dev/mmcblk0p8       /mnt/test4           auto       default,ro            1  0

        test1_re = (
            r"^/dev/[a-z0-9]+%d\s+/mnt/test1\s+auto\s+nouser\s+0\s+2\s*$" % extra_start
        )
        test2_re = r"^/dev/[a-z0-9]+%d\s+/mnt/test2\s+ext4\s+default,ro\s+0\s+2\s*$" % (
            extra_start + 1
        )
        test3_re = r"^/dev/[a-z0-9]+%d\s+/mnt/test3\s+ext4\s+default,ro\s+1\s+2\s*$" % (
            extra_start + 2
        )
        test4_re = r"^/dev/[a-z0-9]+%d\s+/mnt/test4\s+ext4\s+default,ro\s+1\s+0\s*$" % (
            extra_start + 3
        )
        assert re.search(test1_re, fstab, flags=re.MULTILINE) is not None
        assert re.search(test2_re, fstab, flags=re.MULTILINE) is not None
        assert re.search(test3_re, fstab, flags=re.MULTILINE) is not None
        assert re.search(test4_re, fstab, flags=re.MULTILINE) is not None

    @pytest.mark.min_mender_version("2.5.0")
    def test_build_nodbus(self, request, prepared_test_build, bitbake_path):
        """Test that we can remove dbus from PACKAGECONFIG, and that this causes the
        library dependency to be gone. The opposite is not tested, since we
        assume failure to link to the library will be caught in other tests that
        test DBus functionality."""

        build_image(
            prepared_test_build["build_dir"],
            prepared_test_build["bitbake_corebase"],
            "mender-client",
            ['PACKAGECONFIG_remove = "dbus"'],
        )

        env = get_bitbake_variables(
            request, "mender-client", prepared_test_build=prepared_test_build
        )

        # Get dynamic section info from binary.
        output = subprocess.check_output(
            [env["READELF"], "-d", os.path.join(env["D"], "usr/bin/mender")]
        ).decode()

        # Verify the output is sane.
        assert "libc" in output

        # Actual test.
        assert "libglib" not in output

        # Make sure busconfig files are also gone.
        assert not os.path.exists(
            os.path.join(env["D"], "usr/share/dbus-1/system.d/io.mender.conf")
        )
        assert not os.path.exists(
            os.path.join(env["D"], "etc/dbus-1/system.d/io.mender.conf")
        )

    @pytest.mark.min_mender_version("2.5.0")
    @pytest.mark.only_with_image("ext4")
    def test_mender_inventory_network_scripts(
        self, request, prepared_test_build, bitbake_image
    ):
        """
        Test the 'inventory-network-scripts' build feature configuration through
        'PACKAGECONFIG' is working as expected.

        This verifies that the 'inventory-network-scripts' option is a part
        build, and also that the inventory scripts are not included when
        removed.


        The test only runs for sdimg, as the build image should not really matter here.
        """

        #
        # Feature enabled
        #
        reset_build_conf(prepared_test_build["build_dir"])
        build_image(
            prepared_test_build["build_dir"],
            prepared_test_build["bitbake_corebase"],
            bitbake_image,
            ['PACKAGECONFIG_append_pn-mender-client = " inventory-network-scripts"'],
        )
        rootfs = latest_build_artifact(
            request, prepared_test_build["build_dir"], "core-image*.ext4"
        )
        assert len(rootfs) > 0, "rootfs not generated"

        output = subprocess.check_output(
            ["debugfs", "-R", "ls /usr/share/mender/inventory", rootfs]
        )
        assert (
            b"mender-inventory-geo" in output
        ), "mender-inventory-network-scripts seems not to be a part of the image, like they should"

        #
        # Feature disabled
        #
        reset_build_conf(prepared_test_build["build_dir"])
        build_image(
            prepared_test_build["build_dir"],
            prepared_test_build["bitbake_corebase"],
            bitbake_image,
            ['PACKAGECONFIG_remove_pn-mender-client = " inventory-network-scripts"'],
        )
        rootfs = latest_build_artifact(
            request, prepared_test_build["build_dir"], "core-image*.ext4"
        )
        assert len(rootfs) > 0, "ext4 not generated"
        output = subprocess.check_output(
            ["debugfs", "-R", "ls /usr/share/mender/inventory", rootfs]
        )
        assert (
            b"mender-inventory-geo" not in output
        ), "mender-inventory-network-scripts unexpectedly a part of the image"
