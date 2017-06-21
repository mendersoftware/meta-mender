require mender.inc

def mender_branch_from_preferred_version(pref_version):
    if not pref_version:
        return "master"
    else:
        # Return part before "-git", which should be branch name.
        return pref_version[0:pref_version.index("-git")]

MENDER_BRANCH = "${@mender_branch_from_preferred_version(d.getVar('PREFERRED_VERSION'))}"

SRC_URI = "git://github.com/mendersoftware/mender;protocol=https;branch=${MENDER_BRANCH}"

SRCREV ?= "${AUTOREV}"
PV = "${MENDER_BRANCH}-git${SRCPV}"

# DO NOT change the checksum here without make sure that ALL licenses (including
# dependencies) are included in the LICENSE variable below.
LIC_FILES_CHKSUM = "file://LIC_FILES_CHKSUM.sha256;md5=a3dc9721e9e3088f375b677b8af6527a"
LICENSE = "Apache-2.0 & BSD-2-Clause & BSD-3-Clause & MIT & OLDAP-2.8"

# Downprioritize this recipe in version selections.
DEFAULT_PREFERENCE = "-1"
