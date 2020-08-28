FILESEXTRAPATHS_prepend_mender-client-install := "${THISDIR}/files:"

SRC_URI_append_mender-client-install = " file://server.crt"

MENDER_UPDATE_POLL_INTERVAL_SECONDS_mender-client-install = "5"
MENDER_INVENTORY_POLL_INTERVAL_SECONDS_mender-client-install = "5"
MENDER_RETRY_POLL_INTERVAL_SECONDS_mender-client-install = "30"

PACKAGECONFIG_append = "${@mender_feature_is_enabled("mender-client-install", " modules", "", d)}"

MENDER_CERT_LOCATION_mender-client-install ?= "${docdir}/mender-client/examples/demo.crt"

# We need this because the certificate will automatically end up in the
# mender-doc package when placed in ${docdir}.
RDEPENDS_${PN}_append_mender-client-install = " ${PN}-doc"

do_compile_prepend_mender-client-install() {
  bbwarn "You are building with the mender-demo layer, which is not intended for production use"
}
