FILESEXTRAPATHS_prepend := "${THISDIR}/${PN}:"

#TODO: ${@bb.utils.contains("MACHINE_FEATURES", "sd", "packagegroup-mender-sd", "", d)}
#./meta/recipes-core/packagegroups/packagegroup-base.bb
do_install_append () {
    install -d ${D}/u-boot
}
