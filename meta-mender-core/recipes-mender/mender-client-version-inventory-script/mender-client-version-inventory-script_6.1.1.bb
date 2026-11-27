require mender-client-version-inventory-script.inc

################################################################################
#-------------------------------------------------------------------------------
# THINGS TO CONSIDER FOR EACH RELEASE:
# - SRC_URI (particularly "branch")
# - SRCREV
# - DEFAULT_PREFERENCE
#-------------------------------------------------------------------------------

SRC_URI = "git://github.com/mendersoftware/mender-client-subcomponents.git;protocol=https;branch=6.1.x"

# Tag 6.1.1
SRCREV = "18ca6b5569f5c88c972bc11ab969fa2e6bad1df8"

# Enable this in Betas, and in branches that cannot carry this major version as
# default.
# Downprioritize this recipe in version selections.
#DEFAULT_PREFERENCE = "-1"

# Strict dependency checking is enabled by default (build fails on package conflicts).
# When cherry-picking to maintenance branches where the default inventory script's version
# doesn't correspond to the default versions of Mender Client subcomponents, uncomment
# the following line in this directory's mender_%.bbappend:
#       PACKAGECONFIG:remove:pn-mender = "version-inventory-script-strict"
################################################################################

# DO NOT change the checksum here without make sure that ALL licenses (including
# dependencies) are included in the LICENSE variable below.
LIC_FILES_CHKSUM = " \
    file://LICENSE;md5=a8c81350f12516cbb62844f937d81d11 \
"
LICENSE = "Apache-2.0"
