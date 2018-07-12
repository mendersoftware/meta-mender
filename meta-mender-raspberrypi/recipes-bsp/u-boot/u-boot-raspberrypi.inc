FILESEXTRAPATHS_prepend_rpi := "${THISDIR}/patches:"

BOOTENV_SIZE_rpi ?= "0x4000"

SRC_URI_append_rpi = " file://0001-CONFIGS-rpi-enable-mender-requirements.patch"
SRC_URI_remove_rpi = " file://0004-Disable-CONFIG_BOOTCOMMAND-and-enable-CONFIG_MENDER_.patch"
