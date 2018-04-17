#!/bin/bash

set -x -e

. /env.txt

for file in "$BOOTLOADER" "$BOOTLOADER_DATA" "$DISK_IMG"; do
    file="$(basename "$file")"
    if [ -e "/mnt/build/tmp/deploy/images/$MACHINE/$file" ]; then
        cp "/mnt/build/tmp/deploy/images/$MACHINE/$file" /
    fi
done

CONFIG_ARGS=

if [ -f /mnt/config/server.crt ]; then
    CONFIG_ARGS="$CONFIG_ARGS --server-crt=/mnt/config/server.crt"
fi

if [ -f /mnt/config/artifact-verify-key.pem ]; then
    CONFIG_ARGS="$CONFIG_ARGS --verify-key=/mnt/config/artifact-verify-key.pem"
fi

./setup-mender-configuration.py --img="$DISK_IMG" \
                                --server-url=$SERVER_URL \
                                --tenant-token=$TENANT_TOKEN $CONFIG_ARGS

./mender-qemu "$@"
