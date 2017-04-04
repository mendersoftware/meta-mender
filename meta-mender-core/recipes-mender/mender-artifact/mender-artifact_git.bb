require mender-artifact.inc

MENDER_ARTIFACT_BRANCH ?= "master"

SRC_URI = "git://github.com/mendersoftware/mender-artifact.git;protocol=https;branch=${MENDER_ARTIFACT_BRANCH}"

# The revision listed below is not really important, it's just a way to avoid
# network probing during parsing if we are not gonna build the git version
# anyway. If git version is enabled, the AUTOREV will be chosen instead of the
# SHA.
def mender_artifact_is_git_version(d):
    version = d.getVar("PREFERRED_VERSION_${PN}")
    if version is not None and "git" in version:
        return d.getVar("AUTOREV")
    else:
        return "77326b288c70cd713e7ad15d2a084b6ee797e8ff"
SRCREV ?= '${@mender_artifact_is_git_version(d)}'

PV = "${MENDER_ARTIFACT_BRANCH}-git${SRCPV}"

LICENSE = "Apache-2.0"
LIC_FILES_CHKSUM = "file://LIC_FILES_CHKSUM.sha256;md5=f4a3edb2a8fe8e2ecde8062ba20b1c86"

# Downprioritize this recipe in version selections.
DEFAULT_PREFERENCE = "-1"
