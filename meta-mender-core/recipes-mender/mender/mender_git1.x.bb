require mender_git.inc
require mender-old-makefile.inc

def mender_version_of_this_recipe(d, srcpv):
    version = mender_version_from_preferred_version(d, srcpv)
    if version.startswith("1."):
        return version
    else:
        # Post-2.0. We don't want to match this.
        return "non-matching-version-" + version
PV = "${@mender_version_of_this_recipe(d, '${SRCPV}')}"
