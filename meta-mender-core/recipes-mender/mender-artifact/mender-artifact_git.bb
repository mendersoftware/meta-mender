require mender-artifact.inc

MENDER_ARTIFACT_BRANCH ?= "master"

SRC_URI = "git://github.com/mendersoftware/mender-artifact.git;protocol=https;branch=${MENDER_ARTIFACT_BRANCH}"

# The revision listed below is not really important, it's just a way to avoid
# network probing during parsing if we are not gonna build the git version
# anyway. If git version is enabled, the AUTOREV will be chosen instead of the
# SHA.
SRCREV ?= '${@oe.utils.ifelse("git" in d.getVar("PREFERRED_VERSION_${PN}",True), "${AUTOREV}", "77326b288c70cd713e7ad15d2a084b6ee797e8ff")}'
PV = "${MENDER_ARTIFACT_BRANCH}-git${SRCPV}"

LICENSE = "Apache-2.0"
LIC_FILES_CHKSUM = "file://LIC_FILES_CHKSUM.sha256;md5=f4a3edb2a8fe8e2ecde8062ba20b1c86"
