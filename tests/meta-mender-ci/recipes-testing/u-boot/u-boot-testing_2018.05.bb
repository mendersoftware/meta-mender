require u-boot-common_${PV}.inc
require u-boot.inc
require recipes-bsp/u-boot/u-boot-mender.inc

FILESEXTRAPATHS_prepend := "${THISDIR}/patches:"

DEPENDS += "bc-native dtc-native"

INSANE_SKIP_u-boot-testing += "ldflags textrel"

PROVIDES = "u-boot"
RPROVIDES_${PN} = "u-boot"
