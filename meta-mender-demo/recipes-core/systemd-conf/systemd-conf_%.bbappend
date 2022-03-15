FILESEXTRAPATHS:prepend_mender-systemd := "${THISDIR}/files:"

SRC_URI:append_mender-systemd = " \
    file://eth.network \
    file://en.network \
"

FILES:${PN}:append_mender-systemd = " \
    ${sysconfdir}/systemd/network/eth.network \
    ${sysconfdir}/systemd/network/en.network \
"

do_install:append_mender-systemd() {
        install -d ${D}${sysconfdir}/systemd/network
        install -m 0755 ${WORKDIR}/eth.network ${D}${sysconfdir}/systemd/network
        install -m 0755 ${WORKDIR}/en.network ${D}${sysconfdir}/systemd/network
}
