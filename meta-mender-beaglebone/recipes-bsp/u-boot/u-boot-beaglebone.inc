FILESEXTRAPATHS_prepend_beaglebone-yocto := "${THISDIR}/patches:"

SRC_URI_append_beaglebone-yocto = " file://0001-BBB-Use-Mender-boot-code-for-selecting-boot-device-a.patch"

BOOTENV_SIZE_beaglebone-yocto ?= "0x20000"
