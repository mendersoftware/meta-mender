include grub-mender-grubenv.inc

SRC_URI = "${GRUB_MENDER_GRUBENV_SRC_URI}"

SRCREV = "${GRUB_MENDER_GRUBENV_REV}"
PV = "1.3.0+git${SRCREV}"

LICENSE = "Apache-2.0"
LIC_FILES_CHKSUM = "file://LICENSE;md5=7fd64609fe1bce47db0e8f6e3cc6a11d"
