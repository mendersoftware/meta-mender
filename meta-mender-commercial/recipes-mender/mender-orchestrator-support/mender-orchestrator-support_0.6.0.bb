require mender-orchestrator-support.inc

################################################################################
#-------------------------------------------------------------------------------
# THINGS TO CONSIDER FOR EACH RELEASE:
# - SRC_URI (particularly "branch")
# - SRCREV
# - DEFAULT_PREFERENCE
#-------------------------------------------------------------------------------

SRC_URI = "git://github.com/mendersoftware/mender-orchestrator-support;protocol=https;branch=main"

# Tag: 0.6.0
SRCREV = "7a4116727f892e1098a271bb3208e8b7c4d37723"

# Enable this in Betas, and in branches that cannot carry this major version as
# default.
# Downprioritize this recipe in version selections.
#DEFAULT_PREFERENCE = "-1"

################################################################################

# DO NOT change the checksum here without make sure that ALL licenses (including
# dependencies) are included in the LICENSE variable below.
LIC_FILES_CHKSUM = " \
    file://LICENSE;md5=bdb3c11018be1e2200c1c75a15fa7228 \
"
LICENSE = "Apache-2.0"
