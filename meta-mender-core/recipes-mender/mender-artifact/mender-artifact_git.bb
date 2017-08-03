require mender-artifact.inc

def mender_branch_from_preferred_version(pref_version):
    if not pref_version:
        return "master"
    else:
        # Return part before "-git", which should be branch name.
        return pref_version[0:pref_version.index("-git")]

MENDER_ARTIFACT_BRANCH = "${@mender_branch_from_preferred_version(d.getVar('PREFERRED_VERSION'))}"

SRC_URI = "git://github.com/mendersoftware/mender-artifact.git;protocol=https;branch=${MENDER_ARTIFACT_BRANCH}"

# The revision listed below is not really important, it's just a way to avoid
# network probing during parsing if we are not gonna build the git version
# anyway. If git version is enabled, the AUTOREV will be chosen instead of the
# SHA.
def mender_artifact_autorev_if_git_version(d):
    version = d.getVar("PREFERRED_VERSION")
    if version is not None and "git" in version:
        return d.getVar("AUTOREV")
    else:
        return "77326b288c70cd713e7ad15d2a084b6ee797e8ff"
SRCREV ?= '${@mender_artifact_autorev_if_git_version(d)}'

PV = "${MENDER_ARTIFACT_BRANCH}-git${SRCPV}"

# DO NOT change the checksum here without make sure that ALL licenses (including
# dependencies) are included in the LICENSE variable below.
def mender_license(branch):
    if branch == "2.0.x":
        return {
                   "md5": "70480461e7f35d34bbc0b27e02b87311",
                   "license": "Apache-2.0 & BSD-2-Clause & BSD-3-Clause & ISC & MIT",
        }
    else:
        return {
                   "md5": "1baf9ba39aca12f99a87a99b18440e84",
                   "license": "Apache-2.0 & BSD-2-Clause & BSD-3-Clause & ISC & MIT",
        }
LIC_FILES_CHKSUM = "file://LIC_FILES_CHKSUM.sha256;md5=${@mender_license(d.getVar('MENDER_ARTIFACT_BRANCH'))['md5']}"
LICENSE = "${@mender_license(d.getVar('MENDER_ARTIFACT_BRANCH'))['license']}"

# Downprioritize this recipe in version selections.
DEFAULT_PREFERENCE = "-1"
