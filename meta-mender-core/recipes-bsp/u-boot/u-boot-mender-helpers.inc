BOOTENV_SIZE ??= "0x20000"
BOOTENV_SIZE[doc] = "Size of bootloader environment"

MENDER_UBOOT_CONFIG_SYS_MMC_ENV_PART ??= "0"

################################################################################
# Helpers and internal variables.
################################################################################

# @return the full path to the uboot environment device (IE /dev/mmcblkXbootY or /dev/mmcblkX)
def mender_get_uboot_env_mmc_linux_device_path(d):
    # Convert u-boot partition numbers to linux device references
    # See [CONFIG_SYS_MMC_ENV_PART](https://github.com/u-boot/u-boot/blob/u-boot-2016.09.y/README#L4390) and
    # [linux kernel mmc-dev-parts documentation](https://www.kernel.org/doc/Documentation/mmc/mmc-dev-parts.txt)
    storage_device=d.getVar("MENDER_STORAGE_DEVICE",True)
    env_part=d.getVar("MENDER_UBOOT_CONFIG_SYS_MMC_ENV_PART",True)
    env_part_append=""
    if env_part != "0":
        env_part_append="boot%d" % (int(env_part)-1)
    return storage_device + env_part_append

MENDER_UBOOT_MMC_ENV_LINUX_DEVICE_PATH ?= "${@mender_get_uboot_env_mmc_linux_device_path(d)}"

# This should evaluate to the same as MENDER_RESERVED_SPACE_BOOTLOADER_DATA.
# The only reason it's not evaluated the same way is that we don't have the
# necessary information (BOOTENV_SIZE) when evaluating
# MENDER_RESERVED_SPACE_BOOTLOADER_DATA.  Note: If MENDER_UBOOT_CONFIG_SYS_MMC_ENV_PART is set to a non zero value
# MENDER_RESERVED_SPACE_BOOTLOADER_DATA may be set to 0 to remove from rootfs size calculations.
MENDER_BOOTENV_TOTAL_ALIGNED_SIZE = "${@mender_get_env_total_aligned_size(${BOOTENV_SIZE}, ${MENDER_PARTITION_ALIGNMENT})}"

def mender_get_env_offset(start_offset, index, total_aligned_size):
    if index == 1:
        return "0x%x" % int(start_offset)
    elif index == 2:
        return "0x%x" % int(start_offset + total_aligned_size / 2)
    else:
        raise Exception("env index out of range in mender_get_env_offset: Should not happen")

MENDER_UBOOT_ENV_STORAGE_DEVICE_OFFSET_1 ?= "${@mender_get_env_offset(${MENDER_UBOOT_ENV_STORAGE_DEVICE_OFFSET}, 1, \
                                                                      ${MENDER_BOOTENV_TOTAL_ALIGNED_SIZE})}"
MENDER_UBOOT_ENV_STORAGE_DEVICE_OFFSET_2 ?= "${@mender_get_env_offset(${MENDER_UBOOT_ENV_STORAGE_DEVICE_OFFSET}, 2, \
                                                                      ${MENDER_BOOTENV_TOTAL_ALIGNED_SIZE})}"

mender_create_fw_env_config_file() {
    # Takes one argument, which is the file to put it in.

    set -x

    # fw-utils seem to only be able to handle hex values.
    HEX_BOOTENV_SIZE="$(printf 0x%x "${BOOTENV_SIZE}")"

    # create fw_env.config file
    cat > $1 <<EOF
${MENDER_UBOOT_MMC_ENV_LINUX_DEVICE_PATH} ${MENDER_UBOOT_ENV_STORAGE_DEVICE_OFFSET_1} $HEX_BOOTENV_SIZE
${MENDER_UBOOT_MMC_ENV_LINUX_DEVICE_PATH} ${MENDER_UBOOT_ENV_STORAGE_DEVICE_OFFSET_2} $HEX_BOOTENV_SIZE
EOF
}

# UBI specific version of the fw_env.config file.
mender_create_fw_env_config_file_mender-ubi() {
    # Takes one argument, which is the file to put it in.

    set -x

    # fw-utils seem to only be able to handle hex values.
    HEX_BOOTENV_SIZE="$(printf 0x%x "${BOOTENV_SIZE}")"

    # create fw_env.config file
    cat > $1 <<EOF
/dev/${MENDER_STORAGE_DEVICE}_${MENDER_UBOOT_ENV_UBIVOL_NUMBER_1} 0 $HEX_BOOTENV_SIZE ${MENDER_UBI_LEB_SIZE}
/dev/${MENDER_STORAGE_DEVICE}_${MENDER_UBOOT_ENV_UBIVOL_NUMBER_2} 0 $HEX_BOOTENV_SIZE ${MENDER_UBI_LEB_SIZE}
EOF
}
