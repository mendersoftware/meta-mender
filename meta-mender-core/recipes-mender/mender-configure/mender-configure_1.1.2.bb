require mender-configure.inc

################################################################################
#-------------------------------------------------------------------------------
# THINGS TO CONSIDER FOR EACH RELEASE:
# - SRC_URI (particularly "branch")
# - SRCREV
# - DEFAULT_PREFERENCE
#-------------------------------------------------------------------------------

SRC_URI = "git://github.com/mendersoftware/mender-configure-module;protocol=https;branch=1.1.x"

# Tag: 1.1.2
SRCREV = "6aea66dadf9693a9d8ddd3ccaa9aba4f40ebe22b"

# Enable this in Betas, and in branches that cannot carry this major version as
# default.
# Downprioritize this recipe in version selections.
#DEFAULT_PREFERENCE = "-1"

################################################################################

# DO NOT change the checksum here without make sure that ALL licenses (including
# dependencies) are included in the LICENSE variable below.
LIC_FILES_CHKSUM = " \
    file://LICENSE;md5=30b4554c64108561c0cb1c57e8a044f0 \
"
LICENSE = "Apache-2.0"
