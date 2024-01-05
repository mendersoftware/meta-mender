
SRCREV ?= '${@mender_autorev_if_git_version(d)}'

# Force the version of master and feature-branch packages to compare very highly
# to other versions.
PKGV = "${@'999+${PV}' if any(['${PV}'.startswith(p) for p in ['master', 'feature-']]) else '${PV}'}"

MENDER_BRANCH = "${@mender_branch_from_preferred_version(d)}"

SRC_URI = "gitsm://github.com/mendersoftware/mender;protocol=https;branch=${MENDER_BRANCH}"

# Disables the need for every dependency to be checked, for easier development.
_MENDER_DISABLE_STRICT_LICENSE_CHECKING = "1"

# Downprioritize this recipe in version selections.
DEFAULT_PREFERENCE = "-1"

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
    elif version.endswith("-git%"):
        return version[0:-len("-git%")]
    else:
        # Else return master as branch.
        return "master"

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


# DO NOT change the checksum here without make sure that ALL licenses (including
# dependencies) are included in the LICENSE variable below.
def mender_license(branch):
    import re
    if branch.startswith("1."):
        # Golang client
        return {
            "license": "Apache-2.0 & BSD-2-Clause & BSD-3-Clause & ISC & MIT & OLDAP-2.8",
            "license_file": "file://src/github.com/mendersoftware/mender/LICENSE",
        }
    elif branch.startswith("2.") or branch.startswith("3."):
        # Golang client
        return {
            "license": "Apache-2.0 & BSD-2-Clause & BSD-3-Clause & ISC & MIT & OLDAP-2.8",
            "license_file": "file://src/github.com/mendersoftware/mender/LICENSE",
        }
    else:
        # C++ client
        return {
            "license": "Apache-2.0 & MIT & Unlicense",
            "license_file": "file://LICENSE",
        }
LIC_FILES_CHKSUM = " \
    ${@mender_license(d.getVar('MENDER_BRANCH'))['license_file']};md5=30b4554c64108561c0cb1c57e8a044f0 \
"
LICENSE = "${@mender_license(d.getVar('MENDER_BRANCH'))['license']}"

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

