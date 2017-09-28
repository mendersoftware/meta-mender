require mender.inc

SRC_URI = "git://github.com/mendersoftware/mender;protocol=https;branch=1.1.x"

# Tag: 1.1.0
SRCREV = "d4f9db0fe749912c74beeef74f95447774ad8b14"

# DO NOT change the checksum here without make sure that ALL licenses (including
# dependencies) are included in the LICENSE variable below.
LIC_FILES_CHKSUM = "file://src/github.com/mendersoftware/mender/LIC_FILES_CHKSUM.sha256;md5=ec8e15a3ea20289732cca4a7ef643ef8"
LICENSE = "Apache-2.0 & BSD-2-Clause & BSD-3-Clause & MIT & OLDAP-2.8"
