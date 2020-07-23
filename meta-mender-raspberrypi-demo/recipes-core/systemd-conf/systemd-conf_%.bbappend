FILESEXTRAPATHS_prepend_mender-client-install := "${THISDIR}/files:"

SRC_URI_append_mender-client-install = " file://wireless.network"

FILES_${PN}_append_mender-client-install = " \
    ${sysconfdir}/systemd/network/wireless.network \
"

do_install_append_mender-client-install() {
        install -d ${D}${sysconfdir}/systemd/network
        install -m 0755 ${WORKDIR}/wireless.network ${D}${sysconfdir}/systemd/network
}
