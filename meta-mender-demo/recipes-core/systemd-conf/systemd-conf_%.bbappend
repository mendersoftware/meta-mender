FILESEXTRAPATHS_prepend := "${THISDIR}/files:"

SRC_URI += " \
    file://eth.network \
    file://en.network \
"

do_install_append() {
        install -d ${D}${sysconfdir}/systemd/network
        install -m 0755 ${WORKDIR}/eth.network ${D}${sysconfdir}/systemd/network
        install -m 0755 ${WORKDIR}/en.network ${D}${sysconfdir}/systemd/network
}
