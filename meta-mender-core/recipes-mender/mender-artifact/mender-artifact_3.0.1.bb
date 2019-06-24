require mender-artifact.inc

################################################################################
#-------------------------------------------------------------------------------
# THINGS TO CONSIDER FOR EACH RELEASE:
# - SRC_URI (particularly "branch")
# - SRCREV
# - DEFAULT_PREFERENCE
#-------------------------------------------------------------------------------

SRC_URI = "git://github.com/mendersoftware/mender-artifact.git;protocol=https;branch=3.0.x"

# Tag: 3.0.1
SRCREV = "62b933bd1780ff1ae71e3f62a9642901ff335000"

# Enable this in Betas, not in finals.
# Downprioritize this recipe in version selections.
DEFAULT_PREFERENCE = "-1"

################################################################################

LICENSE = "Apache-2.0 & BSD-2-Clause & BSD-3-Clause & ISC & MIT"
LIC_FILES_CHKSUM = "file://src/github.com/mendersoftware/mender-artifact/LIC_FILES_CHKSUM.sha256;md5=3c56d1f34c03d02dc3001a58712e0b7c"

DEPENDS += "xz"
