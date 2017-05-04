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
