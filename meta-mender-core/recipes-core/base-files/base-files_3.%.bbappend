FILESEXTRAPATHS_prepend_mender-image := "${THISDIR}/${PN}:"

do_mender_patch_device() {
    if [ -z "${MENDER_DATA_PART}" ]; then
        bberror "MENDER_DATA_PART not set."
        exit 1
    fi

    if [ -n "${MENDER_BOOT_PART}" ]; then
        sed -i -e 's,@MENDER_BOOT_PART@,${MENDER_BOOT_PART},g' ${S}/fstab
        sed -i -e 's,@MENDER_BOOT_PART_FSTYPE@,${MENDER_BOOT_PART_FSTYPE},g' ${S}/fstab
    else
        bbdebug 2 "MENDER_BOOT_PART not set. Removing from fstab..."
        sed -i '/^@MENDER_BOOT_PART@/ d' ${S}/fstab
    fi

    sed -i -e 's,@MENDER_DATA_PART@,${MENDER_DATA_PART},g' ${S}/fstab
    sed -i -e 's,@MENDER_DATA_PART_FSTYPE@,${MENDER_DATA_PART_FSTYPE},g' ${S}/fstab
}
python() {
    if bb.utils.contains('DISTRO_FEATURES', 'mender-image', True, False, d):
        bb.build.addtask('do_mender_patch_device', 'do_install', 'do_patch', d)
}

do_install_append_mender-image () {
    install -d ${D}/uboot
    install -d ${D}/data
}
