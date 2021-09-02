#!/bin/sh
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
