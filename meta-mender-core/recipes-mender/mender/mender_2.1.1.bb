require mender.inc

################################################################################
#-------------------------------------------------------------------------------
# THINGS TO CONSIDER FOR EACH RELEASE:
# - SRC_URI (particularly "branch")
# - SRCREV
# - DEFAULT_PREFERENCE
#-------------------------------------------------------------------------------

SRC_URI = "git://github.com/mendersoftware/mender;protocol=https;branch=2.1.x"

# Tag: 2.1.1
SRCREV = "53400c6cfd67a6ed28acb906ee2dfb896a4bf474"

# Enable this in Betas, not in finals.
# Downprioritize this recipe in version selections.
DEFAULT_PREFERENCE = "-1"

################################################################################

# DO NOT change the checksum here without make sure that ALL licenses (including
# dependencies) are included in the LICENSE variable below.
LIC_FILES_CHKSUM = "file://src/github.com/mendersoftware/mender/LIC_FILES_CHKSUM.sha256;md5=ffc66184ec5a0831e6f5d99b88784670"
LICENSE = "Apache-2.0 & BSD-2-Clause & BSD-3-Clause & ISC & MIT & OLDAP-2.8"

DEPENDS += "xz"
RDEPENDS_${PN} += "liblzma"

do_compile_ptest_base() {
   # Yocto branches sumo and older fail in Mender version 2.0
   # ptest since it uses some golang features that are only
   # available in newer branches of OE
   true
}
