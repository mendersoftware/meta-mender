FILESEXTRAPATHS:prepend:mender-systemd := "${THISDIR}/files:"

SRC_URI:append:mender-systemd = " \
    file://eth.network \
    file://en.network \
"

FILES:${PN}:append:mender-systemd = " \
    ${sysconfdir}/systemd/network/eth.network \
    ${sysconfdir}/systemd/network/en.network \
"

do_install:append:mender-systemd() {
        install -d ${D}${sysconfdir}/systemd/network
        install -m 0755 ${UNPACKDIR}/eth.network ${D}${sysconfdir}/systemd/network
        install -m 0755 ${UNPACKDIR}/en.network ${D}${sysconfdir}/systemd/network
}
