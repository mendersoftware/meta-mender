#!/bin/bash

set -x -e

if [ -e /mnt/build/tmp/deploy/images/vexpress-qemu/core-image-full-cmdline-vexpress-qemu.sdimg ]; then
    cp /mnt/build/tmp/deploy/images/vexpress-qemu/core-image-full-cmdline-vexpress-qemu.sdimg .
fi
if [ -e /mnt/build/tmp/deploy/images/vexpress-qemu/u-boot.elf ]; then
    cp /mnt/build/tmp/deploy/images/vexpress-qemu/u-boot.elf .
fi

QEMU_SYSTEM_ARM="qemu-system-arm" VEXPRESS_SDIMG="core-image-full-cmdline-vexpress-qemu.sdimg" UBOOT_ELF="u-boot.elf" ./mender-qemu $*
