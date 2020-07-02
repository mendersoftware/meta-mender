include u-boot-mender-helpers.inc

FILES_${PN}_append_mender-uboot = " /data/u-boot/fw_env.config"

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

do_compile_append_mender-uboot() {
    alignment_bytes=${MENDER_PARTITION_ALIGNMENT}
    if [ $(expr ${MENDER_UBOOT_ENV_STORAGE_DEVICE_OFFSET} % $alignment_bytes) -ne 0 ]; then
        bberror "MENDER_UBOOT_ENV_STORAGE_DEVICE_OFFSET must be aligned to" \
                "MENDER_PARTITION_ALIGNMENT"
    fi

    if [ ! -e ${WORKDIR}/fw_env.config.default ]; then
        mender_create_fw_env_config_file ${WORKDIR}/fw_env.config
    else
        cp ${WORKDIR}/fw_env.config.default ${WORKDIR}/fw_env.config
    fi
}

do_install_append_mender-uboot() {
    install -d -m 755 ${D}${sysconfdir}
    ln -sf /data/u-boot/fw_env.config ${D}${sysconfdir}/fw_env.config

    install -d ${D}/data/u-boot
    install -m 0644 ${WORKDIR}/fw_env.config ${D}/data/u-boot/fw_env.config
}
