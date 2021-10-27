require mender-client_git.inc

PV = "${@mender_version_from_preferred_version(d, '${SRCPV}')}"
