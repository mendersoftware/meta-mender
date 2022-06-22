MENDER_CONF[ServerURL] ?= '{"ServerURL":"https://docker.mender.io"}'
MENDER_CONF[UpdatePollIntervalSeconds] ?= '{"UpdatePollIntervalSeconds":5}'
MENDER_CONF[InventoryPollIntervalSeconds] ?= '{"InventoryPollIntervalSeconds":5}'
MENDER_CONF[RetryPollIntervalSeconds] ?= '{"RetryPollIntervalSeconds":30}'

MENDER_CONF[UpdateControlMapExpirationTimeSeconds] ?= '{"UpdateControlMapExpirationTimeSeconds":90}'
MENDER_CONF[UpdateControlMapBootExpirationTimeSeconds] ?= '{"UpdateControlMapBootExpirationTimeSeconds":45}'

MENDER_CONF:append:mender-client-install = " \
    ServerURL \
    UpdatePollIntervalSeconds \
    InventoryPollIntervalSeconds \
    RetryPollIntervalSeconds \
    UpdateControlMapExpirationTimeSeconds \
    UpdateControlMapBootExpirationTimeSeconds \
"

# Depend on mender-server-certificate, which on demo layer installs the demo cert
DEPENDS:append:class-target = " mender-server-certificate"
RDEPENDS:${PN}:append:class-target = " mender-server-certificate"

do_compile:prepend:mender-client-install() {
  bbwarn "You are building with the mender-demo layer, which is not intended for production use"
}
