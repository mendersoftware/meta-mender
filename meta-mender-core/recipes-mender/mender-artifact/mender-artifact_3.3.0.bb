require mender-artifact.inc

################################################################################
#-------------------------------------------------------------------------------
# THINGS TO CONSIDER FOR EACH RELEASE:
# - SRC_URI (particularly "branch")
# - SRCREV
# - DEFAULT_PREFERENCE
#-------------------------------------------------------------------------------

SRC_URI = "git://github.com/mendersoftware/mender-artifact.git;protocol=https;branch=3.3.x"

# Tag: 3.3.0
SRCREV = "b17a7a34da5be5c1e06fd139d94fca7d56b855cb"

# Enable this in Betas, not in finals.
# Downprioritize this recipe in version selections.
#DEFAULT_PREFERENCE = "-1"

################################################################################

LICENSE = "Apache-2.0 & BSD-2-Clause & BSD-3-Clause & ISC & MIT"
LIC_FILES_CHKSUM = "file://src/github.com/mendersoftware/mender-artifact/LIC_FILES_CHKSUM.sha256;md5=99143e34cf23a99976a299da9fa93bcf"

DEPENDS += "xz"
