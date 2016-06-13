FILESEXTRAPATHS_prepend_menderimage := "${THISDIR}/${PN}:"

#TODO: ${@bb.utils.contains("MACHINE_FEATURES", "sd", "packagegroup-mender-sd", "", d)}
#./meta/recipes-core/packagegroups/packagegroup-base.bb

do_patch_device() {
    # Noop if we're not building a mender-image.
    true
}
do_patch_device_menderimage() {
    if [ -z "${MENDER_BOOT_PART}" ] || [ -z "${MENDER_DATA_PART}" ]; then
        bberror "MENDER_BOOT_PART or MENDER_DATA_PART not set."
        exit 1
    fi

    sed -i -e 's,@MENDER_BOOT_PART@,${MENDER_BOOT_PART},g' ${S}/fstab
    sed -i -e 's,@MENDER_DATA_PART@,${MENDER_DATA_PART},g' ${S}/fstab
}
addtask do_patch_device after do_patch before do_install

do_install_append_menderimage () {
    install -d ${D}/uboot
    install -d ${D}/data
}
