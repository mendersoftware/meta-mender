#!/bin/sh
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
#
# Write the systemd machine-id to the bootloader environment
# so that it will persist between updates.
#

set -eu

if [ -x /usr/bin/grub-mender-grubenv-set ]; then
    BOOTENV_PRINT=grub-mender-grubenv-print
    BOOTENV_SET=grub-mender-grubenv-set
else
    BOOTENV_PRINT=fw_printenv
    BOOTENV_SET=fw_setenv
fi

CURRENT_BOOTLOADER_ID=$($BOOTENV_PRINT mender_systemd_machine_id 2>/dev/null | cut -d= -f2)
CURRENT_SYSTEMD_ID=$(cat /etc/machine-id)

rc=0
if [ -z "${CURRENT_BOOTLOADER_ID}" ] && [ ! -z "${CURRENT_SYSTEMD_ID}" ]; then
    $BOOTENV_SET "mender_systemd_machine_id" "${CURRENT_SYSTEMD_ID}"
    rc=$?
elif [ "${CURRENT_BOOTLOADER_ID}" != "${CURRENT_SYSTEMD_ID}" ]; then
    echo "Error; bootloader and systemd disagree on machine-id." >&2
    rc=1
fi

exit $rc
