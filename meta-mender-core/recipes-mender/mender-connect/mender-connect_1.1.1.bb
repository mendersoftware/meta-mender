require mender-connect.inc

RDEPENDS:${PN} = "glib-2.0 mender-client (>= 2.5)"

################################################################################
#-------------------------------------------------------------------------------
# THINGS TO CONSIDER FOR EACH RELEASE:
# - SRC_URI (particularly "branch")
# - SRCREV
# - DEFAULT_PREFERENCE
#-------------------------------------------------------------------------------

SRC_URI = "git://github.com/mendersoftware/mender-connect.git;protocol=https;branch=1.1.x"

# Tag: 1.1.1
SRCREV = "a65c431f19b8dd03b207441e78bc2b6f35a91b85"

# Enable this in Betas, and in branches that cannot carry this major version as
# default.
# Downprioritize this recipe in version selections.
#DEFAULT_PREFERENCE = "-1"

################################################################################

# DO NOT change the checksum here without make sure that ALL licenses (including
# dependencies) are included in the LICENSE variable below. Note that for
# releases, we must check the LIC_FILES_CHKSUM.sha256 file, not the LICENSE
# file.
LICENSE = "Apache-2.0 & BSD-2-Clause & BSD-3-Clause & ISC & MIT"
LIC_FILES_CHKSUM = "file://src/github.com/mendersoftware/mender-connect/LIC_FILES_CHKSUM.sha256;md5=fa1436147d867cccbbc08ed73f77f9b6"
