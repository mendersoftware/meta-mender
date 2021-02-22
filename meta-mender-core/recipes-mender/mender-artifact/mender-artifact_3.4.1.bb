require mender-artifact.inc

################################################################################
#-------------------------------------------------------------------------------
# THINGS TO CONSIDER FOR EACH RELEASE:
# - SRC_URI (particularly "branch")
# - SRCREV
# - DEFAULT_PREFERENCE
#-------------------------------------------------------------------------------

SRC_URI = "git://github.com/mendersoftware/mender-artifact.git;protocol=https;branch=3.4.x"

# Tag: 3.4.1
SRCREV = "25919b61c82392653e921ec0124cde4dd7cfa405"

# Enable this in Betas, not in finals.
# Downprioritize this recipe in version selections.
#DEFAULT_PREFERENCE = "-1"

################################################################################

# DO NOT change the checksum here without make sure that ALL licenses (including
# dependencies) are included in the LICENSE variable below. Note that for
# releases, we must check the LIC_FILES_CHKSUM.sha256 file, not the LICENSE
# file.
LICENSE = "Apache-2.0 & BSD-2-Clause & BSD-3-Clause & ISC & MIT"
LIC_FILES_CHKSUM = "file://src/github.com/mendersoftware/mender-artifact/LIC_FILES_CHKSUM.sha256;md5=7ec199eb2815c1cb147efc754c38d4b1"

DEPENDS += "xz"
