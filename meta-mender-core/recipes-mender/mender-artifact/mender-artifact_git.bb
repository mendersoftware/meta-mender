require mender-artifact.inc

def mender_branch_from_preferred_version(pref_version):
    if not pref_version:
        return "master"
    else:
        # Return part before "-git", which should be branch name.
        return pref_version[0:pref_version.index("-git")]

MENDER_ARTIFACT_BRANCH = "${@mender_branch_from_preferred_version(d.getVar('PREFERRED_VERSION'))}"

SRC_URI = "git://github.com/mendersoftware/mender-artifact.git;protocol=https;branch=${MENDER_ARTIFACT_BRANCH}"

SRCREV ?= "${AUTOREV}"
PV = "${MENDER_ARTIFACT_BRANCH}-git${SRCPV}"

# DO NOT change the checksum here without make sure that ALL licenses (including
# dependencies) are included in the LICENSE variable below.
LICENSE = "Apache-2.0"
LIC_FILES_CHKSUM = "file://LIC_FILES_CHKSUM.sha256;md5=2471b64e22329e03bc6cd52540e8f497"

# Downprioritize this recipe in version selections.
DEFAULT_PREFERENCE = "-1"
