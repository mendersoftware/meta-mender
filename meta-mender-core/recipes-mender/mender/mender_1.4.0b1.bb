require mender.inc

SRC_URI = "git://github.com/mendersoftware/mender;protocol=https;branch=1.4.x"

# Tag: 1.4.0b1
SRCREV = "d24ea6a7e16327f6c4bb29e80d3b11b7529d5e86"

# Enable this in Betas, not in finals.
# Downprioritize this recipe in version selections.
DEFAULT_PREFERENCE = "-1"

# DO NOT change the checksum here without make sure that ALL licenses (including
# dependencies) are included in the LICENSE variable below.
LIC_FILES_CHKSUM = "file://src/github.com/mendersoftware/mender/LIC_FILES_CHKSUM.sha256;md5=13741fb0210ea8a11a3e8e0247c9429c"
LICENSE = "Apache-2.0 & BSD-2-Clause & BSD-3-Clause & MIT & OLDAP-2.8"
