require mender-artifact.inc

DEPENDS += "xz openssl"
RDEPENDS:${PN} = "openssl"

# The revision listed below is not really important, it's just a way to avoid
# network probing during parsing if we are not gonna build the git version
# anyway. If git version is enabled, the AUTOREV will be chosen instead of the
# SHA.
def mender_artifact_autorev_if_git_version(d):
    version = d.getVar("PREFERRED_VERSION")
    if version is None or version == "":
        version = d.getVar("PREFERRED_VERSION:%s" % d.getVar('PN'))
    if not d.getVar("EXTERNALSRC") and version is not None and "git" in version:
        return d.getVar("AUTOREV")
    else:
        return "77326b288c70cd713e7ad15d2a084b6ee797e8ff"
SRCREV ?= '${@mender_artifact_autorev_if_git_version(d)}'

def mender_branch_from_preferred_version(d):
    import re
    version = d.getVar("PREFERRED_VERSION")
    if version is None or version == "":
        version = d.getVar("PREFERRED_VERSION:%s" % d.getVar('PN'))
    if version is None:
        version = ""
    match = re.match(r"^[0-9]+\.[0-9]+\.", version)
    if match is not None:
        # If the preferred version is some kind of version, use the branch name
        # for that one (1.0.x style).
        return match.group(0) + "x"
    elif version.endswith("-git%"):
        return version[0:-len("-git%")]
    else:
        # Else return master as branch.
        return "master"
MENDER_ARTIFACT_BRANCH = "${@mender_branch_from_preferred_version(d)}"

def mender_version_from_preferred_version(d):
    pref_version = d.getVar("PREFERRED_VERSION")
    srcpv = d.getVar("SRCPV")
    if pref_version is None:
        pref_version = d.getVar("PREFERRED_VERSION:%s" % d.getVar("PN"))
    if pref_version is not None and pref_version.find("-git") >= 0:
        # If "-git" is in the version, remove it along with any suffix it has,
        # and then readd it with commit SHA.
        return "%s-git%s" % (pref_version[0:pref_version.index("-git")], srcpv)
    elif pref_version is not None and pref_version.find("-build") >= 0:
        # If "-build" is in the version, use the version as is. This means that
        # we can build tags with "-build" in them from this recipe, but not
        # final tags, which will need their own recipe.
        return pref_version
    else:
        # Else return the default "master-git".
        return "master-git%s" % srcpv
PV = "${@mender_version_from_preferred_version(d)}"

SRC_URI = "git://github.com/mendersoftware/mender-artifact.git;protocol=https;branch=${MENDER_ARTIFACT_BRANCH}"

# DO NOT change the checksum here without make sure that ALL licenses (including
# dependencies) are included in the LICENSE variable below.
def mender_license(branch):
    # Only one currently. If the sub licenses change we may introduce more.
    return {
               "license": "Apache-2.0 & BSD-2-Clause & BSD-3-Clause & ISC & MIT & MPL-2.0",
    }
LIC_FILES_CHKSUM = " \
    file://src/github.com/mendersoftware/mender-artifact/LICENSE;md5=f92624f2343d21e1986ca36f82756029 \
"
LICENSE = "${@mender_license(d.getVar('MENDER_ARTIFACT_BRANCH'))['license']}"

# Disables the need for every dependency to be checked, for easier development.
_MENDER_DISABLE_STRICT_LICENSE_CHECKING = "1"

# Downprioritize this recipe in version selections.
DEFAULT_PREFERENCE = "-1"
