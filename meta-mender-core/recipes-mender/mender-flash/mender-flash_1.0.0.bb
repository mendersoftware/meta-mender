require mender-flash.inc

################################################################################
#-------------------------------------------------------------------------------
# THINGS TO CONSIDER FOR EACH RELEASE:
# - SRC_URI (particularly "branch")
# - SRCREV
# - DEFAULT_PREFERENCE
#-------------------------------------------------------------------------------

SRC_URI = "gitsm://github.com/mendersoftware/mender-flash.git;protocol=https;branch=1.0.x"

# Tag: 1.0.0
SRCREV = "842e984d5ef19e7a539957a6fc31f9a177a7bacd"

# Enable this in Betas, and in branches that cannot carry this major version as
# default.
# Downprioritize this recipe in version selections.
# DEFAULT_PREFERENCE = "-1"

################################################################################

# DO NOT change the checksum here without make sure that ALL licenses (including
# dependencies) are included in the LICENSE variable below. Note that for
# releases, we must check the LIC_FILES_CHKSUM.sha256 file, not the LICENSE
# file.
LICENSE = "Apache-2.0 & CC0-1.0"

LIC_FILES_CHKSUM = " \
    file://LICENSE;md5=b4b4cfdaea6d61aa5793b92efd42e081 \
    file://vendor/expected/COPYING;md5=65d3616852dbf7b1a6d4b53b00626032 \
"
