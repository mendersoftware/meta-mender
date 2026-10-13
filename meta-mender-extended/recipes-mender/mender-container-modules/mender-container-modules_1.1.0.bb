require mender-container-modules.inc

################################################################################
#-------------------------------------------------------------------------------
# THINGS TO CONSIDER FOR EACH RELEASE:
# - SRC_URI (particularly "branch")
# - SRCREV
# - DEFAULT_PREFERENCE
#-------------------------------------------------------------------------------

SRC_URI = "git://github.com/mendersoftware/mender-container-modules.git;protocol=https;branch=1.1.x"

# Tag: 1.1.0
SRCREV = "814b6393189d352dbdabb6e2d5d1890ef0e24ea1"

# Enable this in Betas, and in branches that cannot carry this major version as
# default.
# Downprioritize this recipe in version selections.
# DEFAULT_PREFERENCE = "-1"

################################################################################

# DO NOT change the checksum here without make sure that ALL licenses (including
# dependencies) are included in the LICENSE variable below. Note that for
# releases, we must check the LIC_FILES_CHKSUM.sha256 file, not the LICENSE
# file.
LICENSE = "Apache-2.0"

LIC_FILES_CHKSUM = " \
        file://LICENSE;md5=a8c81350f12516cbb62844f937d81d11 \
"
