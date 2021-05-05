MENDER_UPDATE_POLL_INTERVAL_SECONDS_mender-client-install = "5"
MENDER_INVENTORY_POLL_INTERVAL_SECONDS_mender-client-install = "5"
MENDER_RETRY_POLL_INTERVAL_SECONDS_mender-client-install = "30"

# Depend on mender-server-certificate, which on demo layer installs the demo cert
DEPENDS_append_class-target = " mender-server-certificate"
RDEPENDS_${PN}_append_class-target = " mender-server-certificate"

do_compile_prepend_mender-client-install() {
  bbwarn "You are building with the mender-demo layer, which is not intended for production use"
}
