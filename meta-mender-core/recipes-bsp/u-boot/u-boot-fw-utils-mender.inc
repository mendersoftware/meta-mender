require u-boot-mender-common.inc

inherit deploy

do_compile_append() {
    alignment_bytes=$(expr ${MENDER_PARTITION_ALIGNMENT_KB} \* 1024)
    if [ $(expr ${MENDER_UBOOT_ENV_STORAGE_DEVICE_OFFSET} % $alignment_bytes) -ne 0 ]; then
        bberror "MENDER_UBOOT_ENV_STORAGE_DEVICE_OFFSET must be aligned to" \
                "MENDER_PARTITION_ALIGNMENT_KB"
    fi

    if [ ! -e ${WORKDIR}/fw_env.config.default ]; then
        mender_create_fw_env_config_file ${WORKDIR}/fw_env.config
    else
        cp ${WORKDIR}/fw_env.config.default ${WORKDIR}/fw_env.config
    fi
}

do_install_append() {
    install -d -m 755 ${D}${sysconfdir}
    ln -sf /data/u-boot/fw_env.config ${D}${sysconfdir}/fw_env.config
}

do_deploy() {
    install -d ${WORKDIR}/data/u-boot
    install -m 0644 ${WORKDIR}/fw_env.config ${WORKDIR}/data/u-boot/fw_env.config
    # We need to keep the permissions in a tar file, because they are not
    # remembered by bitbake's fakeroot mechanism if we put it directly in the
    # deploy directory.
    ( cd ${WORKDIR} && tar cf ${WORKDIR}/data.tar --owner=root --group=root data )

    cp ${WORKDIR}/data.tar ${DEPLOYDIR}
}
addtask deploy after do_compile
