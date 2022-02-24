FILESEXTRAPATHS:prepend:mender-client-install := "${THISDIR}/files:"

SRC_URI:append:mender-client-install = " \
	file://mender.io.png \
"

# Explicitly set to all arch/machines, otherwise breaks on raspberrypi builds
# with error "Nothing RPROVIDES 'psplash-raspberrypi'"
SPLASH_IMAGES:mender-client-install:all = "file://mender.io.png;outsuffix=default"
