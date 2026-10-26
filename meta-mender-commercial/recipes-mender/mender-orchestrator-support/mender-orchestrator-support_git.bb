require mender-orchestrator-support.inc

# The revision listed below is not really important, it's just a way to avoid
# network probing during parsing if we are not gonna build the git version
# anyway. If git version is enabled, the AUTOREV will be chosen instead of the
# SHA.
def mender_orchestrator_support_autorev_if_git_version(d):
    version = d.getVar("PREFERRED_VERSION")
    if version is None or version == "":
        version = d.getVar("PREFERRED_VERSION:%s" % d.getVar('PN'))
    if not d.getVar("EXTERNALSRC") and version is not None and "git" in version:
        return d.getVar("AUTOREV")
    else:
        return "a074100cf481ece4e3e201bb75a6b32344e98385"
SRCREV ?= '${@mender_orchestrator_support_autorev_if_git_version(d)}'

def mender_orchestrator_support_branch_from_preferred_version(d):
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
        return "main"
MENDER_ORCHESTRATOR_SUPPORT_BRANCH = "${@mender_orchestrator_support_branch_from_preferred_version(d)}"

def mender_orchestrator_support_version_from_preferred_version(d):
    pref_version = d.getVar("PREFERRED_VERSION")
    srcpv = d.getVar("SRCPV")
    if pref_version is None:
        pref_version = d.getVar("PREFERRED_VERSION:%s" % d.getVar("PN"))
    if pref_version is not None and pref_version.find("-git") >= 0:
        # If "-git" is in the version, remove it along with any suffix it has,
        # and then read it with commit SHA.
        return "%s-git%s" % (pref_version[0:pref_version.index("-git")], srcpv)
    elif pref_version is not None and pref_version.find("-build") >= 0:
        # If "-build" is in the version, use the version as is. This means that
        # we can build tags with "-build" in them from this recipe, but not
        # final tags, which will need their own recipe.
        return pref_version
    else:
        # Else return the default "main-git".
        return "main-git%s" % srcpv
PV = "${@mender_orchestrator_support_version_from_preferred_version(d)}"

SRC_URI = "git://github.com/mendersoftware/mender-orchestrator-support;protocol=https;branch=${MENDER_ORCHESTRATOR_SUPPORT_BRANCH}"

# DO NOT change the checksum here without making sure that ALL licenses (including
# dependencies) are included in the LICENSE variable below.
LIC_FILES_CHKSUM = " \
    file://LICENSE;md5=bdb3c11018be1e2200c1c75a15fa7228 \
"
LICENSE = "Apache-2.0"

# Disables the need for every dependency to be checked, for easier development.
_MENDER_DISABLE_STRICT_LICENSE_CHECKING = "1"

# Downprioritize this recipe in version selections.
DEFAULT_PREFERENCE = "-1"
