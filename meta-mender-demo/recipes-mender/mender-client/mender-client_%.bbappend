FILESEXTRAPATHS_prepend := "${THISDIR}/files:"

SRC_URI_append = " file://server.crt"

MENDER_UPDATE_POLL_INTERVAL_SECONDS = "5"
MENDER_INVENTORY_POLL_INTERVAL_SECONDS = "5"
MENDER_RETRY_POLL_INTERVAL_SECONDS = "30"

MENDER_UPDATE_CONTROL_MAP_EXPIRATION_TIME_SECONDS_mender-client-install = "90"
MENDER_UPDATE_CONTROL_MAP_BOOT_EXPIRATION_TIME_SECONDS_mender-client-install = "45"

PACKAGECONFIG_append = " modules"

MENDER_CERT_LOCATION ?= "${docdir}/mender-client/examples/demo.crt"
# We need this because the certificate will automatically end up in the
# mender-doc package when placed in ${docdir}.
RDEPENDS_${PN}_append = " ${PN}-doc"

do_compile_prepend() {
  bbwarn "You are building with the mender-demo layer, which is not intended for production use"
}
