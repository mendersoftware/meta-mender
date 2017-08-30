FILESEXTRAPATHS_prepend := "${THISDIR}/files:"

SRC_URI_append_beaglebone = " file://uEnv.txt"

do_install_append_beaglebone() {
    install -m 0644 -t ${D}${datadir}/mender-qa ${WORKDIR}/uEnv.txt
}