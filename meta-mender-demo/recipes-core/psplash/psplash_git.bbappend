FILESEXTRAPATHS_prepend_mender-client-install := "${THISDIR}/files:"

SRC_URI_append_mender-client-install = " \
	file://mender.io.png \
"

SPLASH_IMAGES_mender-client-install = "file://mender.io.png;outsuffix=default"
