require mender-flash.inc

################################################################################
#-------------------------------------------------------------------------------
# THINGS TO CONSIDER FOR EACH RELEASE:
# - SRC_URI (particularly "branch")
# - SRCREV
# - DEFAULT_PREFERENCE
#-------------------------------------------------------------------------------

SRC_URI = "gitsm://github.com/mendersoftware/mender-flash.git;protocol=https;branch=master"

# Tag: 1.0.2
SRCREV = "8eea8dcc55266d9a657f9d61dd7aa119aab675ac"

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
    file://LICENSE;md5=30b4554c64108561c0cb1c57e8a044f0 \
    file://vendor/expected/COPYING;md5=65d3616852dbf7b1a6d4b53b00626032 \
"
