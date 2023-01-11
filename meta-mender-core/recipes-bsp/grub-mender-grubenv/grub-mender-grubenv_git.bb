require grub-mender-grubenv.inc

SRC_URI = "${GRUB_MENDER_GRUBENV_SRC_URI}"

SRCREV = "${GRUB_MENDER_GRUBENV_REV}"
PV = "1.3.0+git${SRCREV}"

LICENSE = "Apache-2.0"
LIC_FILES_CHKSUM = "file://LICENSE;md5=b4b4cfdaea6d61aa5793b92efd42e081"
