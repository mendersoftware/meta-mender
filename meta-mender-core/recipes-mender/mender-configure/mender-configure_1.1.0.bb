require mender-configure.inc

################################################################################
#-------------------------------------------------------------------------------
# THINGS TO CONSIDER FOR EACH RELEASE:
# - SRC_URI (particularly "branch")
# - SRCREV
# - DEFAULT_PREFERENCE
#-------------------------------------------------------------------------------

SRC_URI = "git://github.com/mendersoftware/mender-configure-module;protocol=https;branch=1.1.x"

# Tag: 1.1.0
SRCREV = "024f837a331f6c2b2f632382894ed87e663903f9"

# Enable this in Betas, and in branches that cannot carry this major version as
# default.
# Downprioritize this recipe in version selections.
#DEFAULT_PREFERENCE = "-1"

################################################################################

# DO NOT change the checksum here without make sure that ALL licenses (including
# dependencies) are included in the LICENSE variable below.
LIC_FILES_CHKSUM = " \
    file://LICENSE;md5=b4b4cfdaea6d61aa5793b92efd42e081 \
"
LICENSE = "Apache-2.0"
