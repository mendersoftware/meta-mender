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
import json

# Make sure common is imported after fabric, because we override some functions.
from common import *

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
        """Test that IMAGE_BOOTLOADER_FILE causes the bootloader to be embedded
        correctly in the resulting sdimg."""

        loader_file = "bootloader.bin"
        loader_offset = 4
        add_to_local_conf(prepared_test_build, 'IMAGE_BOOTLOADER_FILE = "%s"' % loader_file)
        add_to_local_conf(prepared_test_build, 'IMAGE_BOOTLOADER_BOOTSECTOR_OFFSET = "%d"' % loader_offset)

        new_bb_vars = get_bitbake_variables("core-image-minimal", prepared_test_build['env_setup'])

        loader_dir = new_bb_vars['DEPLOY_DIR_IMAGE']
        loader_path = os.path.join(loader_dir, loader_file)

        run_verbose("mkdir -p %s" % os.path.dirname(loader_path))
        run_verbose("cp /etc/os-release %s" % loader_path)

        run_bitbake(prepared_test_build)

        built_sdimg = latest_build_artifact(prepared_test_build['build_dir'], ".sdimg")

        original = os.open(loader_path, os.O_RDONLY)
        embedded = os.open(built_sdimg, os.O_RDONLY)
        os.lseek(embedded, loader_offset * 512, 0)

        checked = 0
        block_size = 4096
        while True:
            org_read = os.read(original, block_size)
            org_read_size = len(org_read)
            emb_read = os.read(embedded, org_read_size)

            assert(org_read == emb_read), "Embedded bootloader is not identical to the file specified in IMAGE_BOOTLOADER_FILE"

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

        built_rootfs = latest_build_artifact(prepared_test_build['build_dir'], ".ext4")

        assert(os.stat(built_rootfs).st_size == int(bitbake_variables['MENDER_CALC_ROOTFS_SIZE']) * 1024)


    @pytest.mark.only_with_image('ext4', 'ext3', 'ext2')
    @pytest.mark.min_mender_version("1.0.0")
    def test_tenant_token(self, prepared_test_build):
        """Test setting a custom tenant-token"""

        add_to_local_conf(prepared_test_build, 'MENDER_TENANT_TOKEN = "%s"'
                          %  "authtentoken")

        run_bitbake(prepared_test_build)

        built_rootfs = latest_build_artifact(prepared_test_build['build_dir'], ".ext[234]")

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

        built_rootfs = latest_build_artifact(prepared_test_build['build_dir'], ".ext[234]")
        # Copy out the key we just added from the image and use that to
        # verify instead of the original, just to be sure.
        subprocess.check_call(["debugfs", "-R",
                               "dump -p /etc/mender/artifact-verify-key.pem artifact-verify-key.pem",
                               built_rootfs])
        try:
            built_artifact = latest_build_artifact(prepared_test_build['build_dir'], ".mender")
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
            }

            # Check new rootfs.
            built_rootfs = latest_build_artifact(prepared_test_build['build_dir'], ".ext[234]")
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
            built_mender_image = latest_build_artifact(prepared_test_build['build_dir'], ".mender")
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
    @pytest.mark.parametrize('recipe,version', [('mender', version) for version in versions_of_recipe('mender')]
                             + [('mender', None)]
                             + [('mender-artifact-native', version) for version in versions_of_recipe('mender-artifact')]
                             + [('mender-artifact-native', None)])
    def test_preferred_versions(self, prepared_test_build, recipe, version):
        """Most Jenkins builds build with PREFERRED_VERSION set, because we want to
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
    def test_multiple_device_types_compatible(self, prepared_test_build, bitbake_path):
        """Tests that we can include multiple device_types in the artifact."""

        add_to_local_conf(prepared_test_build, 'MENDER_DEVICE_TYPES_COMPATIBLE = "machine1 machine2"')
        run_bitbake(prepared_test_build)

        image = latest_build_artifact(prepared_test_build['build_dir'], '.mender')

        output = run_verbose("mender-artifact read %s" % image, capture=True)
        assert "Compatible devices: '[machine1 machine2]'" in output

        output = subprocess.check_output("tar xOf %s header.tar.gz | tar xOz header-info" % image, shell=True)
        data = json.loads(output)
        assert data["device_types_compatible"] == ["machine1", "machine2"]
