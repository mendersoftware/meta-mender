LICENSE = "Apache-2.0"

FILESEXTRAPATHS:prepend := "${THISDIR}/files:"
SRC_URI = "file://mender-reboot-detector.service file://LICENSE"
LIC_FILES_CHKSUM = "file://LICENSE;md5=0ea4e253cc22ddc22117b9796e5ce5b7"

inherit systemd

SYSTEMD_SERVICE:${PN} = "mender-reboot-detector.service"
FILES:${PN} = "${systemd_unitdir}/system/mender-reboot-detector.service"

RDEPENDS:${PN} = "bash openssh-sshd"

S = "${WORKDIR}/sources"
UNPACKDIR = "${S}"

do_install() {
    install -d ${D}${systemd_unitdir}/system
    install -m 0644 ${UNPACKDIR}/mender-reboot-detector.service ${D}${systemd_unitdir}/system
}
