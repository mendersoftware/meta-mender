#!/bin/bash

set -x -e

if [ -e /mnt/build/tmp/deploy/images/vexpress-qemu/core-image-full-cmdline-vexpress-qemu.sdimg ]; then
    cp /mnt/build/tmp/deploy/images/vexpress-qemu/core-image-full-cmdline-vexpress-qemu.sdimg .
fi
if [ -e /mnt/build/tmp/deploy/images/vexpress-qemu/u-boot.elf ]; then
    cp /mnt/build/tmp/deploy/images/vexpress-qemu/u-boot.elf .
fi

CONFIG_ARGS=

if [ -f /mnt/config/server.crt ]; then
    CONFIG_ARGS="$CONFIG_ARGS --server-crt=/mnt/config/server.crt"
fi

if [ -f /mnt/config/artifact-verify-key.pem ]; then
    CONFIG_ARGS="$CONFIG_ARGS --verify-key=/mnt/config/artifact-verify-key.pem"
fi

./setup-mender-configuration.py --sdimg=core-image-full-cmdline-vexpress-qemu.sdimg --server-url=$SERVER_URL --tenant-token=$TENANT_TOKEN $CONFIG_ARGS

QEMU_SYSTEM_ARM="qemu-system-arm" VEXPRESS_SDIMG="core-image-full-cmdline-vexpress-qemu.sdimg" UBOOT_ELF="u-boot.elf" ./mender-qemu $*
