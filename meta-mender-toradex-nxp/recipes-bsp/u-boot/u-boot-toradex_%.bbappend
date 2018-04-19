require recipes-bsp/u-boot/u-boot-mender.inc

FILESEXTRAPATHS_prepend := "${THISDIR}/patches:"

SRC_URI_remove = "file://0003-Integration-of-Mender-boot-code-into-U-Boot.patch"
SRC_URI_append = " file://0001-Integration-of-Mender-boot-code-into-U-Boot-v2016.11.patch"

RPROVIDES_${PN} += "u-boot"
BOOTENV_SIZE = "0x18000"
