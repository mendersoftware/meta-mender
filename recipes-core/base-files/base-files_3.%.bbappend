FILESEXTRAPATHS_prepend := "${@bb.utils.contains('DISTRO_FEATURES', 'mender-image', '${THISDIR}/${PN}:', '', d)}"

#TODO: ${@bb.utils.contains("MACHINE_FEATURES", "sd", "packagegroup-mender-sd", "", d)}
#./meta/recipes-core/packagegroups/packagegroup-base.bb

do_patch_device() {
    if ! ${@bb.utils.contains('DISTRO_FEATURES', 'mender-image', 'true', 'false', d)}; then
        exit 0
    fi

    if [ -z "${MENDER_BOOT_PART}" ] || [ -z "${MENDER_DATA_PART}" ]; then
        bberror "MENDER_BOOT_PART or MENDER_DATA_PART not set."
        exit 1
    fi

    sed -i -e 's,@MENDER_BOOT_PART@,${MENDER_BOOT_PART},g' ${S}/fstab
    sed -i -e 's,@MENDER_DATA_PART@,${MENDER_DATA_PART},g' ${S}/fstab
}
addtask do_patch_device after do_patch before do_install

do_install_append () {
    if ! ${@bb.utils.contains('DISTRO_FEATURES', 'mender-image', 'true', 'false', d)}; then
        exit 0
    fi

    install -d ${D}/uboot
    install -d ${D}/data
}
