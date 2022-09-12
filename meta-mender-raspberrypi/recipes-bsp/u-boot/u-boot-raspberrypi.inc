FILESEXTRAPATHS:prepend:rpi := "${THISDIR}/patches:"

BOOTENV_SIZE:rpi ?= "0x4000"

# U-Boot auto-configuration doesn't work properly for Raspberry Pi, due to its
# use of boot.scr and cmdline.txt.
MENDER_UBOOT_AUTO_CONFIGURE:rpi = "0"

SRC_URI:append:rpi:mender-uboot = "${@bb.utils.contains('MENDER_UBOOT_AUTO_CONFIGURE', \
                                                        '1', \
                                                        '', \
                                                        ' file://0001-configs-rpi-enable-mender-requirements.patch \
                                                        ', \
                                                        d)}"
