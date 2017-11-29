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
                # should be empty.
                output = subprocess.check_output(["debugfs", "-R", "ls -p /etc/mender/scripts", latest_rootfs])
                for line in output.split('\n'):
                    if len(line) == 0:
                        continue

                    entry = line.split('/')
                    assert entry[5] == "." or entry[5] == "..", "There should be no file in /etc/mender/scripts"
                break

        # Check artifact.
        output = subprocess.check_output("tar xOf %s header.tar.gz| tar tz"
                                         % latest_mender_image, shell=True)
        for line in output.strip().split('\n'):
            if line == "scripts":
                output = subprocess.check_output("tar xOf %s header.tar.gz| tar tz scripts"
                                                 % latest_mender_image, shell=True)
                assert len(output.strip()) == 0, "Unexpected scripts in base image: %s" % output

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
