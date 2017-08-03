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

import os
import pytest
import subprocess

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
    def test_default_server_certificate(self):
        """Test that the md5sum we have on record matches the server certificate.
        This makes sure the warning about this certificate is correct."""

        output = subprocess.check_output(["md5sum", "../../meta-mender-demo/recipes-mender/mender/files/server.crt"])

        # Crude check, just make sure it occurs in the build file.
        subprocess.check_call("fgrep %s ../../meta-mender-core/recipes-mender/mender/mender.inc >/dev/null 2>&1"
                              % output.split()[0], shell=True)


    def test_bootloader_embed(self, prepared_test_build):
        """Test that IMAGE_BOOTLOADER_FILE causes the bootloader to be embedded
        correctly in the resulting sdimg."""

        fd = open(prepared_test_build['local_conf'], "a")
        loader_file = "bootloader.bin"
        loader_offset = 4
        fd.write('IMAGE_BOOTLOADER_FILE = "%s"\n' % loader_file)
        fd.write('IMAGE_BOOTLOADER_BOOTSECTOR_OFFSET = "%d"\n' % loader_offset)
        fd.close()

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
