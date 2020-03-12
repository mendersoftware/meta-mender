require mender-client_git.inc

def mender_version_of_this_recipe(d, srcpv):
    version = mender_version_from_preferred_version(d, srcpv)
    if version.startswith("1."):
        # Pre-2.0. We don't want to match this.
        return "non-matching-version-" + version
    else:
        return version
PV = "${@mender_version_of_this_recipe(d, '${SRCPV}')}"


# If building from 'externalsrc' with client version
# 2.1.x, 2.2.x, or 2.3.x, the systemd service file is
# still called 'mender' with no client extension.
def mender_client_service_name(d, srcpv):
    version = mender_version_from_preferred_version(d, srcpv)
    if version.startswith("2.1"):
        return "mender"
    elif version.startswith("2.2"):
        return "mender"
    elif version.startswidth("2.3"):
        return "mender"
    return "mender-client"




# MEN-2948: systemd service for the client is now named mender-client.service
MENDER_CLIENT="${@mender_client_service_name(d, '${SRCPV}')}"
