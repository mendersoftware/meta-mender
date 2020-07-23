FILESEXTRAPATHS_prepend_mender-client-install := "${THISDIR}/files:"

SRC_URI_append_mender-client-install = " \
    file://eth.network \
    file://en.network \
"

FILES_${PN}_append_mender-client-install = " \
    ${sysconfdir}/systemd/network/eth.network \
    ${sysconfdir}/systemd/network/en.network \
"

do_install_append_mender-client-install() {
        install -d ${D}${sysconfdir}/systemd/network
        install -m 0755 ${WORKDIR}/eth.network ${D}${sysconfdir}/systemd/network
        install -m 0755 ${WORKDIR}/en.network ${D}${sysconfdir}/systemd/network
}
