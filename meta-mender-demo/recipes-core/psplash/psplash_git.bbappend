FILESEXTRAPATHS:prepend:mender-update-install := "${THISDIR}/files:"

SRC_URI:append:mender-update-install = " \
	file://mender.io.png \
"

# Explicitly set to all arch/machines, otherwise breaks on raspberrypi builds
# with error "Nothing RPROVIDES 'psplash-raspberrypi'"
SPLASH_IMAGES:mender-update-install:all = "file://mender.io.png;outsuffix=default"
