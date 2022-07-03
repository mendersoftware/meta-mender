#!/bin/bash
# Copyright 2022 Northern.tech AS
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

set -x -e

. /env.txt

# For SaaS platform.
[ -s /saas/extensions.sh ] && source /saas/extensions.sh

for file in "$BOOTLOADER" "$BOOTLOADER_DATA" "$DISK_IMG"; do
    if [ -z "$file" ]; then
        continue
    fi
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

# Extract Docker IP and exclude loopback address.
DOCKER_IP="$(ip addr | sed -ne '/^ *inet /{/127\.0\.0\.1/d;s/^ *inet  *\([^ ]*\) .*/\1/;p}')"

if [ ! -e /mender-setup-complete ]; then
    ./setup-mender-configuration.py --img="$DISK_IMG" \
                                    --server-url=$SERVER_URL \
                                    --server-ip=$SERVER_IP \
                                    --tenant-token=$TENANT_TOKEN $CONFIG_ARGS \
                                    --docker-ip="$DOCKER_IP" \
                                    --mender-gateway-conffile "$MENDER_GATEWAY_CONFFILE"
    touch /mender-setup-complete
fi

export QEMU_NET_HOSTFWD=",hostfwd=tcp::80-:80,hostfwd=tcp::85-:85,hostfwd=tcp::443-:443,hostfwd=tcp::8080-:8080"
./mender-qemu "$@"
