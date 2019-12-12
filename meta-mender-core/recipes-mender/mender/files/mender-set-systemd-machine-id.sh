#!/bin/sh
#
# Write the systemd machine-id to the bootloader environment
# so that it will persist between updates.
#

set -eu

CURRENT_BOOTLOADER_ID=$(fw_printenv mender_systemd_machine_id 2>/dev/null | cut -d= -f2)
CURRENT_SYSTEMD_ID=$(cat /etc/machine-id)

rc=0
if [ -z "${CURRENT_BOOTLOADER_ID}" ] && [ ! -z "${CURRENT_SYSTEMD_ID}" ]; then
    fw_setenv "mender_systemd_machine_id" "${CURRENT_SYSTEMD_ID}"
    rc=$?
elif [ "${CURRENT_BOOTLOADER_ID}" != "${CURRENT_SYSTEMD_ID}" ]; then
    echo "Error; bootloader and systemd disagree on machine-id." >&2
    rc=1
fi

exit $rc
