MENDER_UPDATE_POLL_INTERVAL_SECONDS:mender-update-install = "5"
MENDER_INVENTORY_POLL_INTERVAL_SECONDS:mender-update-install = "5"
MENDER_RETRY_POLL_INTERVAL_SECONDS:mender-update-install = "30"

# Depend on mender-server-certificate, which on demo layer installs the demo cert
DEPENDS:append:class-target = " mender-server-certificate"
RDEPENDS:mender-auth:append:class-target = " mender-server-certificate"

RRECOMMENDS:mender-update += "mender-snapshot"

do_compile:prepend() {
  bbwarn "You are building with the mender-demo layer, which is not intended for production use"
}
