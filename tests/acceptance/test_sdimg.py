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

from fabric.api import *

import pytest
import subprocess
import os

# Make sure common is imported after fabric, because we override some functions.
from common import *

class EmbeddedBootloader:
    loader = None
    offset = 0

    def __init__(self, loader, offset):
        self.loader = loader
        self.offset = offset

@pytest.fixture(scope="session")
def embedded_bootloader():
    assert(os.environ.get('BUILDDIR', False), "BUILDDIR must be set")

    current_dir = os.open(".", os.O_RDONLY)
    os.chdir(os.environ['BUILDDIR'])

    output = subprocess.Popen(["bitbake", "-e", "core-image-minimal"], stdout=subprocess.PIPE)
    loader_base = None
    loader_dir = None
    loader = None
    offset = 0
    for line in output.stdout:
        line = line.strip()
        if line.startswith('IMAGE_BOOTLOADER_FILE="') and line.endswith('"'):
            loader_base = line.split('=', 2)[1][1:-1]
        elif line.startswith('IMAGE_BOOTLOADER_BOOTSECTOR_OFFSET="') and line.endswith('"'):
            offset = int(line.split('=', 2)[1][1:-1]) * 512
        elif line.startswith('DEPLOY_DIR_IMAGE="') and line.endswith('"'):
            loader_dir = line.split('=', 2)[1][1:-1]

    if loader_base is not None and loader_base != "":
        loader = os.path.join(loader_dir, loader_base)

    output.wait()
    os.fchdir(current_dir)

    return EmbeddedBootloader(loader, offset)

class TestSdimg:
    def test_bootloader_embed(self, embedded_bootloader, latest_sdimg):
        """Test that IMAGE_BOOTLOADER_FILE causes the bootloader to be embedded
        correctly in the resulting sdimg. If the variable has not been defined,
        the test is skipped."""

        if embedded_bootloader.loader is None:
            pytest.skip("No embedded bootloader specified")

        original = os.open(embedded_bootloader.loader, os.O_RDONLY)
        embedded = os.open(latest_sdimg, os.O_RDONLY)
        os.lseek(embedded, embedded_bootloader.offset, 0)

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
