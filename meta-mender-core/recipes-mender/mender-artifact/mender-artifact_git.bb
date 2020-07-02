require mender-artifact.inc

DEPENDS += "xz"

# The revision listed below is not really important, it's just a way to avoid
# network probing during parsing if we are not gonna build the git version
# anyway. If git version is enabled, the AUTOREV will be chosen instead of the
# SHA.
def mender_artifact_autorev_if_git_version(d):
    version = d.getVar("PREFERRED_VERSION")
    if version is None or version == "":
        version = d.getVar("PREFERRED_VERSION_%s" % d.getVar('PN'))
    if not d.getVar("EXTERNALSRC") and version is not None and "git" in version:
        return d.getVar("AUTOREV")
    else:
        return "77326b288c70cd713e7ad15d2a084b6ee797e8ff"
SRCREV ?= '${@mender_artifact_autorev_if_git_version(d)}'

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
MENDER_ARTIFACT_BRANCH = "${@mender_branch_from_preferred_version(d)}"

def mender_version_from_preferred_version(d, srcpv):
    pref_version = d.getVar("PREFERRED_VERSION")
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
PV = "${@mender_version_from_preferred_version(d, '${SRCPV}')}"

SRC_URI = "git://github.com/mendersoftware/mender-artifact.git;protocol=https;branch=${MENDER_ARTIFACT_BRANCH}"

# DO NOT change the checksum here without make sure that ALL licenses (including
# dependencies) are included in the LICENSE variable below.
def mender_license(branch):
    if branch == "3.1.x" or branch == "3.2.x":
        return {
                   "md5": "f3d4710343f1b959e4fa6b728ce12264",
                   "license": "Apache-2.0 & BSD-2-Clause & BSD-3-Clause & ISC & MIT",
        }
    elif branch == "3.3.x":
        return {
                   "md5": "99143e34cf23a99976a299da9fa93bcf",
                   "license": "Apache-2.0 & BSD-2-Clause & BSD-3-Clause & ISC & MIT",
        }
    elif branch == "3.4.x":
        return {
                   "md5": "d1fedd6e15ea779ce58fafea700f0c37",
                   "license": "Apache-2.0 & BSD-2-Clause & BSD-3-Clause & ISC & MIT",
        }
    else:
        return {
                   "md5": "f93bdbf4b2f555c93363a0ea3d3934b7",
                   "license": "Apache-2.0 & BSD-2-Clause & BSD-3-Clause & ISC & MIT",
        }
LIC_FILES_CHKSUM = "file://src/github.com/mendersoftware/mender-artifact/LIC_FILES_CHKSUM.sha256;md5=${@mender_license(d.getVar('MENDER_ARTIFACT_BRANCH'))['md5']}"
LICENSE = "${@mender_license(d.getVar('MENDER_ARTIFACT_BRANCH'))['license']}"

# Downprioritize this recipe in version selections.
DEFAULT_PREFERENCE = "-1"
