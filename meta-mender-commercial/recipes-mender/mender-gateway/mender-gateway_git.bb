require mender-gateway.inc

inherit mender-closed-source-utils

SRCREV = "${@mender_closed_source_srcrev_from_src_uri(d, '${SRC_URI}', 'mender-gateway')}"

PV = "${@mender_closed_source_pv_from_preferred_version(d, '${SRCREV}')}"

def tarball_directory_from_pv(d, pv):
    return pv.split("master-git+")[-1]

# Define S to work both on git sha and "master" tarballs
S = "${WORKDIR}/mender-gateway-${@tarball_directory_from_pv(d, '${PV}')}"

# Skip version check
MENDER_DEVMODE = "true"

# Downprioritize this recipe in version selections.
DEFAULT_PREFERENCE = "-1"
