require u-boot-common_${PV}.inc
require u-boot.inc
require recipes-bsp/u-boot/u-boot-mender.inc

FILESEXTRAPATHS:prepend := "${THISDIR}/patches:"

DEPENDS += "bc-native dtc-native"

INSANE_SKIP:u-boot-testing += "ldflags textrel"

PROVIDES = "u-boot"
RPROVIDES:${PN} = "u-boot"
