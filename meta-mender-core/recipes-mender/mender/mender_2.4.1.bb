require mender.inc

################################################################################
#-------------------------------------------------------------------------------
# THINGS TO CONSIDER FOR EACH RELEASE:
# - SRC_URI (particularly "branch")
# - SRCREV
# - DEFAULT_PREFERENCE
#-------------------------------------------------------------------------------

SRC_URI = "git://github.com/mendersoftware/mender;protocol=https;branch=2.4.x"

# Tag: 2.4.1
SRCREV = "ffef645f932dd2fd7545705288f6e6df14417966"

# Enable this in Betas, not in finals.
# Downprioritize this recipe in version selections.
#DEFAULT_PREFERENCE = "-1"

################################################################################

# DO NOT change the checksum here without make sure that ALL licenses (including
# dependencies) are included in the LICENSE variable below.
LIC_FILES_CHKSUM = "file://src/github.com/mendersoftware/mender/LIC_FILES_CHKSUM.sha256;md5=5649992d13a6fda40abfac7730a62b07"
LICENSE = "Apache-2.0 & BSD-2-Clause & BSD-3-Clause & ISC & MIT & OLDAP-2.8"

DEPENDS += "xz openssl"
RDEPENDS_${PN} += "liblzma openssl"
