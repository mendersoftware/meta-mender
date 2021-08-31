require mender-client_git.inc

PV = "${@mender_version_from_preferred_version(d, '${SRCPV}')}"

# MEN-2948: systemd service for the client is now named mender-client.service,
# but it was called mender.service in 2.2 and earlier.
def mender_client_name(d):
    if d.getVar("PV")[0:4] in ["2.0.", "2.1.", "2.2."]:
        return "mender"
    else:
        return "mender-client"

MENDER_CLIENT = "${@mender_client_name(d)}"
