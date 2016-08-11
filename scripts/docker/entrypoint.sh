#!/bin/bash
QEMU_SYSTEM_ARM="qemu-system-arm" VEXPRESS_SDIMG="core-image-full-cmdline-vexpress-qemu.sdimg" UBOOT_ELF="u-boot.elf" ./mender-qemu $*
