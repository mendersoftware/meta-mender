#!/usr/bin/python
# Copyright 2018 Northern.tech AS
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

# Make sure common is imported after fabric, because we override some functions.
from common import *

@pytest.mark.usefixtures("no_image_file", "setup_board", "bitbake_path")
class TestInventory:

    @pytest.mark.min_mender_version('1.6.0')
    def test_rootfs_type(self, bitbake_variables):
        """Test that rootfs is returned correctly by the inventory script."""

        if not env.host_string:
            # This means we are not inside execute(). Recurse into it!
            execute(self.test_rootfs_type, bitbake_variables)
            return

        output = run("/usr/share/mender/inventory/mender-inventory-rootfs-type").strip()
        assert(output == "rootfs_type=%s" % bitbake_variables['ARTIFACTIMG_FSTYPE'])

    @pytest.mark.min_mender_version('1.6.0')
    def test_bootloader_integration(self, bitbake_variables):
        """Test that the bootloader integration type matches what we would
        expect from the build."""

        if not env.host_string:
            # This means we are not inside execute(). Recurse into it!
            execute(self.test_bootloader_integration, bitbake_variables)
            return

        features = bitbake_variables['DISTRO_FEATURES'].split()
        arch = bitbake_variables['HOST_ARCH']

        output = run("/usr/share/mender/inventory/mender-inventory-bootloader-integration").strip()
        if arch == "x86_64":
            if "mender-bios" in features:
                assert(output == "mender_bootloader_integration=bios_grub")
            else:
                assert(output == "mender_bootloader_integration=uefi_grub")
        elif arch == "arm":
            if "mender-grub" in features:
                assert(output == "mender_bootloader_integration=uboot_uefi_grub")
            else:
                assert(output == "mender_bootloader_integration=uboot")
        else:
            pytest.fail("Unknown platform combination. Please add a test case for this combination.")
