#!/bin/bash

set -x -e

MACHINE=${MACHINE:-"vexpress-qemu"}
IMAGE=${IMAGE:-"core-image-full-cmdline"}

case "$MACHINE" in
    vexpress-qemu)
        if [ -e /mnt/build/tmp/deploy/images/${MACHINE}/${IMAGE}-${MACHINE}.sdimg ]; then
            cp /mnt/build/tmp/deploy/images/${MACHINE}/${IMAGE}-${MACHINE}.sdimg .
        fi
        VEXPRESS_IMG="${IMAGE}-${MACHINE}.sdimg"
        ;;
    vexpress-qemu-flash)
        if [ -e /mnt/build/tmp/deploy/images/${MACHINE}/${IMAGE}-${MACHINE}.vexpress-nor ]; then
            cp /mnt/build/tmp/deploy/images/${MACHINE}/${IMAGE}-${MACHINE}.vexpress-nor .
        fi
        VEXPRESS_IMG="${IMAGE}-${MACHINE}.vexpress-nor"
        ;;
    *)
        echo "unsupported machine $MACHINE"
        exit 1
        ;;
esac

# NOTE: vexpress-qemu-flash has a differently configured u-boot
if [ -e /mnt/build/tmp/deploy/images/${MACHINE}/u-boot.elf ]; then
    cp /mnt/build/tmp/deploy/images/${MACHINE}/u-boot.elf .
fi

CONFIG_ARGS=

if [ -f /mnt/config/server.crt ]; then
    CONFIG_ARGS="$CONFIG_ARGS --server-crt=/mnt/config/server.crt"
fi

if [ -f /mnt/config/artifact-verify-key.pem ]; then
    CONFIG_ARGS="$CONFIG_ARGS --verify-key=/mnt/config/artifact-verify-key.pem"
fi

if [ "$MACHINE" = "vexpress-qemu" ]; then
    ./setup-mender-configuration.py --sdimg=core-image-full-cmdline-vexpress-qemu.sdimg \
                                    --server-url=$SERVER_URL \
                                    --tenant-token=$TENANT_TOKEN $CONFIG_ARGS
else
    if [ -n "$TENANT_TOKEN" -o -n "$CONFIG_ARGS" -o -n "$SERVER_URL" ]; then
       echo "reconfiguration of flash images is not supported"
       exit 1
    fi
fi

QEMU_SYSTEM_ARM="qemu-system-arm" VEXPRESS_IMG="${VEXPRESS_IMG}" UBOOT_ELF="u-boot.elf" ./mender-qemu $*
