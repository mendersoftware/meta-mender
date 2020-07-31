FILESEXTRAPATHS_prepend_mender-systemd := "${THISDIR}/files:"

SRC_URI_append_mender-systemd = " file://wireless.network"

FILES_${PN}_append_mender-systemd = " \
    ${sysconfdir}/systemd/network/wireless.network \
"

do_install_append_mender-systemd() {
        install -d ${D}${sysconfdir}/systemd/network
        install -m 0755 ${WORKDIR}/wireless.network ${D}${sysconfdir}/systemd/network
}
