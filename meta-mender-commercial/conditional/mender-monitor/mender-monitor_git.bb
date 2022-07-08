require mender-monitor.inc

inherit mender-closed-source-utils

SRCREV = "${@mender_closed_source_srcrev_from_src_uri(d, '${SRC_URI}', 'mender-monitor')}"

PV = "${@mender_closed_source_pv_from_preferred_version(d, '${SRCREV}')}"

# Skip version check
MENDER_DEVMODE = "true"

# Downprioritize this recipe in version selections.
DEFAULT_PREFERENCE = "-1"
