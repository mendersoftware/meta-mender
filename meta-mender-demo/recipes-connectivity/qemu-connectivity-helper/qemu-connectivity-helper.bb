LICENSE = "Apache-2.0"

FILESEXTRAPATHS:prepend := "${THISDIR}/files:"
SRC_URI = "file://qemu-connectivity-helper.service file://LICENSE"
LIC_FILES_CHKSUM = "file://LICENSE;md5=4cd0c347af5bce5ccf3b3d5439a2ea87  "

inherit systemd

SYSTEMD_SERVICE:${PN} = "qemu-connectivity-helper.service"
FILES:${PN} = "${systemd_unitdir}/system/qemu-connectivity-helper.service"

S = "${WORKDIR}/sources"
UNPACKDIR = "${S}"

do_install() {
    install -d ${D}${systemd_unitdir}/system
    install -m 0644 ${WORKDIR}/qemu-connectivity-helper.service ${D}${systemd_unitdir}/system
}
