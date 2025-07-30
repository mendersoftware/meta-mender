LICENSE = "Apache-2.0"

FILESEXTRAPATHS:prepend := "${THISDIR}/files:"
SRC_URI = "file://boot-script.service file://boot-script.sh file://LICENSE"

LIC_FILES_CHKSUM = "file://LICENSE;md5=0ea4e253cc22ddc22117b9796e5ce5b7"
FILES:${PN} += "${sbindir}/boot-script.sh ${systemd_unitdir}/system/boot-script.service"

inherit systemd

SYSTEMD_SERVICE:${PN} = "boot-script.service"

S = "${WORKDIR}/sources"
UNPACKDIR = "${S}"

do_install() {
    install -d ${D}${sbindir}
    install -m 0755 ${UNPACKDIR}/boot-script.sh ${D}${sbindir}

    install -d ${D}${systemd_unitdir}/system
    install -m 0644 ${UNPACKDIR}/boot-script.service ${D}${systemd_unitdir}/system
}
