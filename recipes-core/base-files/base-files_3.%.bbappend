FILESEXTRAPATHS_prepend_menderimage := "${THISDIR}/${PN}:"

#TODO: ${@bb.utils.contains("MACHINE_FEATURES", "sd", "packagegroup-mender-sd", "", d)}
#./meta/recipes-core/packagegroups/packagegroup-base.bb

do_patch_device() {
    # Noop if we're not building a mender-image.
    true
}
do_patch_device_menderimage() {
    if [ -n "${MENDER_STORAGE_DEVICE_BASE}" ]; then
        sed -i -e 's,/dev/mmcblk0p,${MENDER_STORAGE_DEVICE_BASE},g' ${S}/fstab
    fi
}
addtask do_patch_device after do_patch before do_install

do_install_append_menderimage () {
    install -d ${D}/uboot
    install -d ${D}/data
}
