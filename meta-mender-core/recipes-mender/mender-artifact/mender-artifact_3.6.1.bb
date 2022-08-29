require mender-artifact.inc

################################################################################
#-------------------------------------------------------------------------------
# THINGS TO CONSIDER FOR EACH RELEASE:
# - SRC_URI (particularly "branch")
# - SRCREV
# - DEFAULT_PREFERENCE
#-------------------------------------------------------------------------------

SRC_URI = "git://github.com/mendersoftware/mender-artifact.git;protocol=https;branch=3.6.x"

# Tag: 3.6.1
SRCREV = "af2a3e3fb0069df3297dfea78e258c4b4d9dbd4d"

# Enable this in Betas, and in branches that cannot carry this major version as
# default.
# Downprioritize this recipe in version selections.
#DEFAULT_PREFERENCE = "-1"

################################################################################

# DO NOT change the checksum here without make sure that ALL licenses (including
# dependencies) are included in the LICENSE variable below.
LICENSE = "Apache-2.0 & BSD-2-Clause & BSD-3-Clause & ISC & MIT"
LIC_FILES_CHKSUM = " \
    file://src/github.com/mendersoftware/mender-artifact/LICENSE;md5=fbe9cd162201401ffbb442445efecfdc \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/minio/sha256-simd/LICENSE;md5=3b83ef96387f14655fc854ddc3c6bd57 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/mendersoftware/progressbar/LICENSE;md5=dcac2e5bf81a6fe99b034aaaaf1b2019 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/pkg/errors/LICENSE;md5=6fe682a02df52c6653f33bd0f7126b5a \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/pmezard/go-difflib/LICENSE;md5=e9a2ebb8de779a07500ddecca806145e \
    file://src/github.com/mendersoftware/mender-artifact/vendor/golang.org/x/sys/LICENSE;md5=5d4950ecb7b26d2c5e4e7b4e0dd74707 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/golang.org/x/crypto/LICENSE;md5=5d4950ecb7b26d2c5e4e7b4e0dd74707 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/remyoudompheng/go-liblzma/LICENSE;md5=f262c0c06bdd810a85575e1eaeb96e91 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/klauspost/compress/LICENSE;md5=f6eed50d75781660de81b193021f14a2 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/russross/blackfriday/v2/LICENSE.txt;md5=ecf8a8a60560c35a862a4a545f2db1b3 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/davecgh/go-spew/LICENSE;md5=c06795ed54b2a35ebeeb543cd3a73e56 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/stretchr/testify/LICENSE;md5=188f01994659f3c0d310612333d2a26f \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/urfave/cli/LICENSE;md5=c542707ca9fc0b7802407ba62310bd8f \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/sirupsen/logrus/LICENSE;md5=8dadfef729c08ec4e631c4f6fc5d43a0 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/klauspost/pgzip/LICENSE;md5=a6862811c790a468c5d82d68e717c154 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/cpuguy83/go-md2man/v2/LICENSE.md;md5=80794f9009df723bbc6fe19234c9f517 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/shurcooL/sanitized_anchor_name/LICENSE;md5=c670c44b8d826e9b7b99077e5c7ba283 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/gopkg.in/yaml.v3/LICENSE;md5=3c91c17266710e16afdbb2b6d15c761c \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/mattn/go-isatty/LICENSE;md5=f509beadd5a11227c27b5d2ad6c9f2c6 \
"

DEPENDS += "xz"
