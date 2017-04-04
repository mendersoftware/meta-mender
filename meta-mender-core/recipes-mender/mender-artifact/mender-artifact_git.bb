require mender-artifact.inc

MENDER_ARTIFACT_BRANCH ?= "master"

SRC_URI = "git://github.com/mendersoftware/mender-artifact.git;protocol=https;branch=${MENDER_ARTIFACT_BRANCH}"

SRCREV ?= "${AUTOREV}"
PV = "${MENDER_ARTIFACT_BRANCH}-git${SRCPV}"

# DO NOT change the checksum here without make sure that ALL licenses (including
# dependencies) are included in the LICENSE variable below.
LICENSE = "Apache-2.0"
LIC_FILES_CHKSUM = "file://LIC_FILES_CHKSUM.sha256;md5=f4a3edb2a8fe8e2ecde8062ba20b1c86"

# Downprioritize this recipe in version selections.
DEFAULT_PREFERENCE = "-1"
