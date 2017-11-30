FILESEXTRAPATHS_prepend_rpi := "${THISDIR}/patches:"

BOOTENV_SIZE_rpi ?= "0x4000"

# U-Boot auto-configuration doesn't work properly for Raspberry Pi, due to its
# use of boot.scr and cmdline.txt.
MENDER_UBOOT_AUTO_CONFIGURE ?= "0"

SRC_URI_append_rpi = "${@bb.utils.contains('MENDER_UBOOT_AUTO_CONFIGURE', \
                                           '1', \
                                           '', \
                                           ' file://0001-CONFIGS-rpi-enable-mender-requirements.patch', \
                                           d)}"
