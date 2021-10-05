require mender-client.inc

################################################################################
#-------------------------------------------------------------------------------
# THINGS TO CONSIDER FOR EACH RELEASE:
# - SRC_URI (particularly "branch")
# - SRCREV
# - DEFAULT_PREFERENCE
#-------------------------------------------------------------------------------

SRC_URI = "git://github.com/mendersoftware/mender;protocol=https;branch=3.0.x"

# Tag: 3.0.1
SRCREV = "90da1266710ba89f061e511d3e2cb46a7258088f"

# Enable this in Betas, and in branches that cannot carry this major version as
# default.
# Downprioritize this recipe in version selections.
DEFAULT_PREFERENCE = "-1"

################################################################################

# DO NOT change the checksum here without make sure that ALL licenses (including
# dependencies) are included in the LICENSE variable below. Note that for
# releases, we must check the LIC_FILES_CHKSUM.sha256 file, not the LICENSE
# file.
LIC_FILES_CHKSUM = "file://src/github.com/mendersoftware/mender/LIC_FILES_CHKSUM.sha256;md5=69a48b331ae876b6775139310ec72f1b"
LICENSE = "Apache-2.0 & BSD-2-Clause & BSD-3-Clause & ISC & MIT & OLDAP-2.8 & OpenSSL"

DEPENDS += "xz openssl"
RDEPENDS_${PN} += "liblzma openssl"
