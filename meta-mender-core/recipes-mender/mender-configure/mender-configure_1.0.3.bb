require mender-configure.inc

################################################################################
#-------------------------------------------------------------------------------
# THINGS TO CONSIDER FOR EACH RELEASE:
# - SRC_URI (particularly "branch")
# - SRCREV
# - DEFAULT_PREFERENCE
#-------------------------------------------------------------------------------

SRC_URI = "git://github.com/mendersoftware/mender-configure-module;protocol=https;branch=1.0.x"

# TODO: tag still not commited
# Tag candidate: 1.0.3
SRCREV = "04337acc040bf6ee2821def68effba1d561f4de1"

# Enable this in Betas, and in branches that cannot carry this major version as
# default.
# Downprioritize this recipe in version selections.
#DEFAULT_PREFERENCE = "-1"

################################################################################

# DO NOT change the checksum here without make sure that ALL licenses (including
# dependencies) are included in the LICENSE variable below. Note that for
# releases, we must check the LIC_FILES_CHKSUM.sha256 file, not the LICENSE
# file.
LIC_FILES_CHKSUM = "file://${S}/LIC_FILES_CHKSUM.sha256;md5=3c1272b686bf6c7e080db5ba294298ed"
LICENSE = "Apache-2.0"
