# Provide boot file specifically for booting from USB to Flash a Mender image.

FILESEXTRAPATHS_prepend := "${THISDIR}/files:"

SRC_URI_append = " file://boot-for-flashing.cmd"

do_compile_append() {
    mkimage -A arm -T script -C none -n "Boot script for flashing Mender image" -d "${WORKDIR}/boot-for-flashing.cmd" boot-for-flashing.scr
}

do_deploy_append() {
    install -m 644 boot-for-flashing.scr ${DEPLOYDIR}
}
