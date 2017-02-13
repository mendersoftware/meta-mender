require mender.inc

MENDER_BRANCH ?= "master"

SRC_URI = "git://github.com/mendersoftware/mender;protocol=https;branch=${MENDER_BRANCH}"

# The revision listed below is not really important, it's just a way to avoid
# network probing during parsing if we are not gonna build the git version
# anyway. If git version is enabled, the AUTOREV will be chosen instead of the
# SHA.
SRCREV ?= '${@oe.utils.ifelse("git" in d.getVar("PREFERRED_VERSION_mender"), "${AUTOREV}", "f6ffa190892202263fdb75975059fbb201adab6a")}'
PV = "${MENDER_BRANCH}-git${SRCPV}"

# DO NOT change the checksum here without make sure that ALL licenses (including
# dependencies) are included in the LICENSE variable below.
LIC_FILES_CHKSUM = "file://LIC_FILES_CHKSUM.sha256;md5=ec8e15a3ea20289732cca4a7ef643ef8"
LICENSE = "Apache-2.0 & BSD-2-Clause & BSD-3-Clause & MIT & OLDAP-2.8"
