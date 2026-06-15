require u-boot-common_${PV}.inc
require u-boot.inc
require recipes-bsp/u-boot/u-boot-mender.inc

FILESEXTRAPATHS:prepend := "${THISDIR}/patches:"

DEPENDS += "bc-native dtc-native bison-native gnutls-native python3-pyelftools-native"

INSANE_SKIP:u-boot-testing += "ldflags textrel buildpaths"

PROVIDES = "u-boot"
RPROVIDES:${PN} = "u-boot"
