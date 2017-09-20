require mender.inc

SRC_URI = "git://github.com/mendersoftware/mender;protocol=https;branch=1.2.x"

# Tag: 1.2.1
SRCREV = "e8899d80f40c409297e15baabb671445286cb84e"

# DO NOT change the checksum here without make sure that ALL licenses (including
# dependencies) are included in the LICENSE variable below.
LIC_FILES_CHKSUM = "file://LIC_FILES_CHKSUM.sha256;md5=13741fb0210ea8a11a3e8e0247c9429c"
LICENSE = "Apache-2.0 & BSD-2-Clause & BSD-3-Clause & MIT & OLDAP-2.8"
