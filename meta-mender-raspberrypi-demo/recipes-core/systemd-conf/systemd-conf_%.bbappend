FILESEXTRAPATHS:prepend_mender-systemd := "${THISDIR}/files:"

SRC_URI:append_mender-systemd = " file://wireless.network"

FILES:${PN}:append_mender-systemd = " \
    ${sysconfdir}/systemd/network/wireless.network \
"

do_install:append_mender-systemd() {
        install -d ${D}${sysconfdir}/systemd/network
        install -m 0755 ${WORKDIR}/wireless.network ${D}${sysconfdir}/systemd/network
}
