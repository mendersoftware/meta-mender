require mender-snapshot.inc

################################################################################
#-------------------------------------------------------------------------------
# THINGS TO CONSIDER FOR EACH RELEASE:
# - SRC_URI (particularly "branch")
# - SRCREV
# - DEFAULT_PREFERENCE
#-------------------------------------------------------------------------------

SRC_URI = "git://github.com/mendersoftware/mender-snapshot.git;protocol=https;branch=1.0.x;destsuffix=${GO_SRCURI_DESTSUFFIX}"

# Tag: 1.0.0
SRCREV = "6f451781ec252fa9d40f04301aad1b2faa98905f"

# Enable this in Betas, and in branches that cannot carry this major version as
# default.
# Downprioritize this recipe in version selections.
# DEFAULT_PREFERENCE = "-1"

################################################################################

# DO NOT change the checksum here without make sure that ALL licenses (including
# dependencies) are included in the LICENSE variable below. Note that for
# releases, we must check the LIC_FILES_CHKSUM.sha256 file, not the LICENSE
# file.
LICENSE = "Apache-2.0 & BSD-2-Clause & BSD-3-Clause & MIT"

LIC_FILES_CHKSUM = " \
    file://src/github.com/mendersoftware/mender-snapshot/LICENSE;md5=30b4554c64108561c0cb1c57e8a044f0 \
    file://src/github.com/mendersoftware/mender-snapshot/vendor/github.com/mendersoftware/progressbar/LICENSE;md5=dcac2e5bf81a6fe99b034aaaaf1b2019 \
    file://src/github.com/mendersoftware/mender-snapshot/vendor/golang.org/x/sys/LICENSE;md5=5d4950ecb7b26d2c5e4e7b4e0dd74707 \
    file://src/github.com/mendersoftware/mender-snapshot/vendor/golang.org/x/term/LICENSE;md5=5d4950ecb7b26d2c5e4e7b4e0dd74707 \
    file://src/github.com/mendersoftware/mender-snapshot/vendor/github.com/pkg/errors/LICENSE;md5=6fe682a02df52c6653f33bd0f7126b5a \
    file://src/github.com/mendersoftware/mender-snapshot/vendor/github.com/cpuguy83/go-md2man/v2/LICENSE.md;md5=80794f9009df723bbc6fe19234c9f517 \
    file://src/github.com/mendersoftware/mender-snapshot/vendor/github.com/urfave/cli/v2/LICENSE;md5=c542707ca9fc0b7802407ba62310bd8f \
    file://src/github.com/mendersoftware/mender-snapshot/vendor/github.com/sirupsen/logrus/LICENSE;md5=8dadfef729c08ec4e631c4f6fc5d43a0 \
    file://src/github.com/mendersoftware/mender-snapshot/vendor/github.com/mattn/go-isatty/LICENSE;md5=f509beadd5a11227c27b5d2ad6c9f2c6 \
    file://src/github.com/mendersoftware/mender-snapshot/vendor/github.com/ungerik/go-sysfs/LICENSE;md5=8dcf593007db59ad07e54ff7908726d2 \
    file://src/github.com/mendersoftware/mender-snapshot/vendor/github.com/russross/blackfriday/v2/LICENSE.txt;md5=ecf8a8a60560c35a862a4a545f2db1b3 \
"
