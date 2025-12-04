################################################################################
# This is a tentative recipe for next Mender Client release
#

require mender-client-version-inventory-script.inc

################################################################################
#-------------------------------------------------------------------------------
# THINGS TO CONSIDER FOR EACH RELEASE:
# - SRC_URI (particularly "branch")
# - SRCREV
# - DEFAULT_PREFERENCE
#-------------------------------------------------------------------------------

SRC_URI = "git://github.com/mendersoftware/mender-client-subcomponents.git;protocol=https;branch=future"

SRCREV = "593fc22312bee04f95beb2a44f9640874c1c1a43"

# Enable this in Betas, and in branches that cannot carry this major version as
# default.
# Downprioritize this recipe in version selections.
#DEFAULT_PREFERENCE = "-1"

################################################################################

# DO NOT change the checksum here without make sure that ALL licenses (including
# dependencies) are included in the LICENSE variable below.
LIC_FILES_CHKSUM = " \
    file://LICENSE;md5=f92624f2343d21e1986ca36f82756029 \
"
LICENSE = "Apache-2.0"
