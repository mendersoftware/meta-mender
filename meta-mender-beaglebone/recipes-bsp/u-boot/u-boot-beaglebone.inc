FILESEXTRAPATHS_prepend_beaglebone := "${THISDIR}/patches:"

SRC_URI_append_beaglebone = " file://0001-BBB-Use-Mender-boot-code-for-selecting-boot-device-a.patch"

BOOTENV_SIZE_beaglebone ?= "0x20000"
