require mender-artifact.inc

################################################################################
#-------------------------------------------------------------------------------
# THINGS TO CONSIDER FOR EACH RELEASE:
# - SRC_URI (particularly "branch")
# - SRCREV
# - DEFAULT_PREFERENCE
#-------------------------------------------------------------------------------

SRC_URI = "git://github.com/mendersoftware/mender-artifact.git;protocol=https;branch=2.4.x"

# Tag: 2.4.1
SRCREV = "574bb9802cdf5f9b4c96d460925e55089c39d009"

# Enable this in Betas, not in finals.
# Downprioritize this recipe in version selections.
#DEFAULT_PREFERENCE = "-1"

################################################################################

LICENSE = "Apache-2.0 & BSD-2-Clause & BSD-3-Clause & ISC & MIT"
LIC_FILES_CHKSUM = "file://src/github.com/mendersoftware/mender-artifact/LIC_FILES_CHKSUM.sha256;md5=8ce3d9108b58e4a185a5f812536f03a5"
