FILESEXTRAPATHS:prepend:mender-systemd := "${THISDIR}/files:"

SRC_URI:append:mender-systemd = " file://wireless.network"

FILES:${PN}:append:mender-systemd = " \
    ${sysconfdir}/systemd/network/wireless.network \
"

do_install:append:mender-systemd() {
        install -d ${D}${sysconfdir}/systemd/network
        install -m 0755 ${WORKDIR}/wireless.network ${D}${sysconfdir}/systemd/network
}
