# This script is shared between the normal shell and Grub shell, so make sure it
# is compatible with both.

function mender_check_grubenv_valid {
    if [ "${mender_boot_part}" != "${mender_rootfsa_part}" -a "${mender_boot_part}" != "${mender_rootfsb_part}" ]; then
        return 1
    fi

    if [ "${bootcount}" != "0" -a "${bootcount}" != "1" ]; then
        return 1
    fi

    if [ "${upgrade_available}" != "0" -a "${upgrade_available}" != "1" ]; then
        return 1
    fi

    return 0
}
