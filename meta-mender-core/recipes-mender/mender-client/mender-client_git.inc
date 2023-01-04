require mender-client.inc

DEPENDS = "xz openssl"
RDEPENDS:${PN} = "liblzma openssl"

# 3.4 and older mender-client versions need mender-artifact-info.
RDEPENDS:${PN}:append = "${@mender_maybe_artifact_info(d)}"

def mender_maybe_artifact_info(d):
    import re
    branch = d.getVar("MENDER_BRANCH")
    match = re.match(r"([0-9]+)\.([0-9]+)\.", branch)
    if match is None:
        return ""

    major = int(match.group(1))
    minor = int(match.group(2))
    if major < 3 or (major == 3 and minor < 5):
        return " mender-artifact-info"
    else:
        return ""

# The revision listed below is not really important, it's just a way to avoid
# network probing during parsing if we are not gonna build the git version
# anyway. If git version is enabled, the AUTOREV will be chosen instead of the
# SHA.
def mender_autorev_if_git_version(d):
    version = d.getVar("PREFERRED_VERSION")
    if version is None or version == "":
        version = d.getVar("PREFERRED_VERSION_%s" % d.getVar('PN'))
    if not d.getVar("EXTERNALSRC") and version is not None and "git" in version:
        return d.getVar("AUTOREV")
    else:
        return "f6ffa190892202263fdb75975059fbb201adab6a"
SRCREV ?= '${@mender_autorev_if_git_version(d)}'

# Force the version of master and feature-branch packages to compare very highly
# to other versions.
PKGV = "${@'999+${PV}' if any(['${PV}'.startswith(p) for p in ['master', 'feature-']]) else '${PV}'}"

def mender_branch_from_preferred_version(d):
    import re
    version = d.getVar("PREFERRED_VERSION")
    if version is None or version == "":
        version = d.getVar("PREFERRED_VERSION_%s" % d.getVar('PN'))
    if version is None:
        version = ""
    match = re.match(r"^[0-9]+\.[0-9]+\.", version)
    if match is not None:
        # If the preferred version is some kind of version, use the branch name
        # for that one (1.0.x style).
        return match.group(0) + "x"
    else:
        # Else return master as branch.
        return "master"
MENDER_BRANCH = "${@mender_branch_from_preferred_version(d)}"

def mender_version_from_preferred_version(d):
    pref_version = d.getVar("PREFERRED_VERSION")
    srcpv = d.getVar("SRCPV")
    if pref_version is None:
        pref_version = d.getVar("PREFERRED_VERSION_%s" % d.getVar("PN"))
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

SRC_URI = "git://github.com/mendersoftware/mender;protocol=https;branch=${MENDER_BRANCH}"

# DO NOT change the checksum here without make sure that ALL licenses (including
# dependencies) are included in the LICENSE variable below.
def mender_license(branch):
    import re
    if branch.startswith("1."):
        return {
                   "license": "Apache-2.0 & BSD-2-Clause & BSD-3-Clause & ISC & MIT & OLDAP-2.8",
        }
    else:
        return {
                   "license": "Apache-2.0 & BSD-2-Clause & BSD-3-Clause & ISC & MIT & OLDAP-2.8",
        }
LIC_FILES_CHKSUM = " \
    file://src/github.com/mendersoftware/mender/LICENSE;md5=b4b4cfdaea6d61aa5793b92efd42e081 \
"
LICENSE = "${@mender_license(d.getVar('MENDER_BRANCH'))['license']}"

# Disables the need for every dependency to be checked, for easier development.
_MENDER_DISABLE_STRICT_LICENSE_CHECKING = "1"

# Downprioritize this recipe in version selections.
DEFAULT_PREFERENCE = "-1"
