require mender-monitor.inc

PV = "master-git"

# Source directly the repo, override name
S = "${WORKDIR}/monitor-client"

# Skip version check
MENDER_DEVMODE = "true"

# Downprioritize this recipe in version selections.
DEFAULT_PREFERENCE = "-1"
