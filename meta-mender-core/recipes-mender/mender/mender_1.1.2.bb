require mender.inc

SRC_URI = "git://github.com/mendersoftware/mender;protocol=https;branch=1.1.x"

# Tag: 1.1.2
SRCREV = "f701559034c32e9fd289fe2a9dc01dff7a8f8d4e"

# DO NOT change the checksum here without make sure that ALL licenses (including
# dependencies) are included in the LICENSE variable below.
LIC_FILES_CHKSUM = "file://src/github.com/mendersoftware/mender/LIC_FILES_CHKSUM.sha256;md5=76c423d4ae33f8df4070f6f58187eeed"
LICENSE = "Apache-2.0 & BSD-2-Clause & BSD-3-Clause & MIT & OLDAP-2.8"
