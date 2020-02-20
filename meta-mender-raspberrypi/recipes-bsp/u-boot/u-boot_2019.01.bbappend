FILESEXTRAPATHS_prepend := "${THISDIR}/${PN}-${PV}:"
SRC_URI_append_raspberrypi4 = " file://0001-configs-rpi4-mender-integration.patch"
SRC_URI_append_rpi = " file://0001-Disable-addition-of-simple-framebuffer-by-U-boot.patch"
