FILESEXTRAPATHS_prepend := "${THISDIR}/patches:"

SRC_URI_append_beaglebone = " file://0001-Disable-feature-which-breaks-internal-MMC-detection.patch"
