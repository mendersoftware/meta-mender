require u-boot-common_${PV}.inc
require u-boot.inc
require recipes-bsp/u-boot/u-boot-mender.inc

FILESEXTRAPATHS_prepend := "${THISDIR}/patches:"

# For tests to recognize the binary by looking for a special string.
SRC_URI += "file://add-test-string.patch"

DEPENDS += "bc-native dtc-native"

INSANE_SKIP_u-boot-testing += "ldflags textrel"

PROVIDES = "u-boot"
RPROVIDES_${PN} = "u-boot"
