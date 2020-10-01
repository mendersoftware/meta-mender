FILESEXTRAPATHS_prepend_mender-client-install := "${THISDIR}/files:"

SRC_URI_append_mender-client-install = " \
	file://mender.io.png \
"

# Explicitly set to all arch/machines, otherwise breaks on raspberrypi builds
# with error "Nothing RPROVIDES 'psplash-raspberrypi'"
SPLASH_IMAGES_mender-client-install_all = "file://mender.io.png;outsuffix=default"
