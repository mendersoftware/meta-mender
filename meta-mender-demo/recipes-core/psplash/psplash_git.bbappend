FILESEXTRAPATHS_prepend := "${THISDIR}/files:"

SRC_URI_append = " \
	file://mender.io.png \
"

SPLASH_IMAGES = "file://mender.io.png;outsuffix=default"
