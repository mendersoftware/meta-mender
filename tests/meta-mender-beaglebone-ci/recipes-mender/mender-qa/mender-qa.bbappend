FILESEXTRAPATHS_prepend := "${THISDIR}/files:"

SRC_URI_append_beaglebone-yocto = " file://uEnv.txt"

do_install_append_beaglebone-yocto() {
    install -m 0644 -t ${D}${datadir}/mender-qa ${WORKDIR}/uEnv.txt
}