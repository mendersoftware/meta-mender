FILESEXTRAPATHS_prepend := "${THISDIR}/files:"

SRC_URI += " file://wireless.network"

FILES_${PN} += " \
    ${sysconfdir}/systemd/network/wireless.network \
"

do_install_append() {
        install -d ${D}${sysconfdir}/systemd/network
        install -m 0755 ${WORKDIR}/wireless.network ${D}${sysconfdir}/systemd/network
}
