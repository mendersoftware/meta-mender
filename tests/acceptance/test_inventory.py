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

import os

import pytest

from utils.common import put_no_sftp


@pytest.mark.usefixtures("setup_board", "bitbake_path")
class TestInventory:
    @pytest.mark.min_mender_version("1.6.0")
    def test_rootfs_type(self, bitbake_variables, connection):
        """Test that rootfs is returned correctly by the inventory script."""

        output = connection.run(
            "/usr/share/mender/inventory/mender-inventory-rootfs-type"
        ).stdout.strip()
        assert output == "rootfs_type=%s" % bitbake_variables["ARTIFACTIMG_FSTYPE"]

    @pytest.mark.min_mender_version("1.6.0")
    def test_bootloader_integration(self, bitbake_variables, connection):
        """Test that the bootloader integration type matches what we would
        expect from the build."""

        features = bitbake_variables["DISTRO_FEATURES"].split()
        arch = bitbake_variables["HOST_ARCH"]

        output = connection.run(
            "/usr/share/mender/inventory/mender-inventory-bootloader-integration"
        ).stdout.strip()
        if arch == "x86_64":
            if "mender-bios" in features:
                assert output == "mender_bootloader_integration=bios_grub"
            else:
                assert output == "mender_bootloader_integration=uefi_grub"
        elif arch == "arm":
            if "mender-grub" in features:
                assert output == "mender_bootloader_integration=uboot_uefi_grub"
            else:
                assert output == "mender_bootloader_integration=uboot"
        else:
            pytest.fail(
                "Unknown platform combination. Please add a test case for this combination."
            )

    @pytest.mark.min_mender_version("2.0.0")
    def test_inventory_os(self, bitbake_variables, connection):
        """Test that "os" inventory attribute is reported correctly by the
        inventory script."""

        sources = [
            {
                "name": "/etc/os-release",
                "content": """NAME="Ubuntu"
VERSION="16.04.4 LTS (Xenial Xerus)"
ID=ubuntu
ID_LIKE=debian
PRETTY_NAME="Ubuntu 16.04.4 LTS"
VERSION_ID="16.04"
HOME_URL="http://www.ubuntu.com/"
SUPPORT_URL="http://help.ubuntu.com/"
BUG_REPORT_URL="http://bugs.launchpad.net/ubuntu/"
VERSION_CODENAME=xenial
UBUNTU_CODENAME=xenial""",
                "mode": 0o644,
                "expected": "os=Ubuntu 16.04.4 LTS",
            },
            {
                "name": "/usr/lib/os-release",
                "content": """ID="poky"
NAME="Poky (Yocto Project Reference Distro)"
VERSION="2.5+snapshot-20180731 (master)"
VERSION_ID="2.5-snapshot-20180731"
""",
                "mode": 0o644,
                "expected": "os=Poky (Yocto Project Reference Distro) 2.5+snapshot-20180731 (master)",
            },
            {
                "name": "/bin/lsb_release",
                "content": """#!/bin/sh
echo Base LSB OS""",
                "mode": 0o755,
                "expected": "os=Base LSB OS",
            },
            {
                "name": "/usr/bin/lsb_release",
                "content": """#!/bin/sh
echo LSB OS""",
                "mode": 0o755,
                "expected": "os=LSB OS",
            },
            {
                "name": "/etc/issue",
                "content": "Issue OS",
                "mode": 0o644,
                "expected": "os=Issue OS",
            },
            {"name": None, "expected": "os=unknown"},
        ]
        for file in [src["name"] for src in sources if src["name"]]:
            backup = "/data%s.backup" % file
            bdir = os.path.dirname(backup)
            connection.run(
                "mkdir -p %s && if [ -e %s ]; then cp %s %s; fi"
                % (bdir, file, file, backup)
            )

        try:
            for src in sources:
                if src.get("name") is None:
                    continue
                with open("tmpfile", "w") as fd:
                    fd.write(src["content"])
                    if src["content"][-1] != "\n":
                        # Write a final newline if there isn't one.
                        fd.write("\n")
                try:
                    put_no_sftp("tmpfile", connection, remote=src["name"])
                    connection.run("chmod 0%o %s" % (src["mode"], src["name"]))
                finally:
                    os.remove("tmpfile")

            for src in sources:
                output = connection.run(
                    "/usr/share/mender/inventory/mender-inventory-os"
                ).stdout.rstrip("\n")
                assert output == src["expected"]
                if src.get("name") is not None:
                    connection.run("rm -f $(realpath %s)" % src["name"])
        finally:
            for file in [src["name"] for src in sources if src["name"]]:
                backup = "/data%s.backup" % file
                connection.run(
                    "if [ -e %s ]; then dd if=%s of=$(realpath %s); fi"
                    % (backup, backup, file)
                )
