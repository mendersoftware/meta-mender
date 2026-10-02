require mender-snapshot.inc

################################################################################
#-------------------------------------------------------------------------------
# THINGS TO CONSIDER FOR EACH RELEASE:
# - SRC_URI (particularly "branch")
# - SRCREV
# - DEFAULT_PREFERENCE
#-------------------------------------------------------------------------------

SRC_URI = "git://github.com/mendersoftware/mender-snapshot.git;protocol=https;destsuffix=${GO_SRCURI_DESTSUFFIX};branch=master"

# Tag: 1.0.1
SRCREV = "4bd932aa1f90cb01ad15fdb601a1e6f6dfdd9f49"

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
    file://src/github.com/mendersoftware/mender-snapshot/LICENSE;md5=a8c81350f12516cbb62844f937d81d11 \
    file://src/github.com/mendersoftware/mender-snapshot/vendor/github.com/mendersoftware/progressbar/LICENSE;md5=f4a60996eb58eca8e4aede01250758e6 \
    file://src/github.com/mendersoftware/mender-snapshot/vendor/golang.org/x/sys/LICENSE;md5=7998cb338f82d15c0eff93b7004d272a \
    file://src/github.com/mendersoftware/mender-snapshot/vendor/golang.org/x/term/LICENSE;md5=7998cb338f82d15c0eff93b7004d272a \
    file://src/github.com/mendersoftware/mender-snapshot/vendor/github.com/pkg/errors/LICENSE;md5=6fe682a02df52c6653f33bd0f7126b5a \
    file://src/github.com/mendersoftware/mender-snapshot/vendor/github.com/stretchr/testify/internal/difflib/LICENSE;md5=37bee94299cc4febcbc4c52da854074d \
    file://src/github.com/mendersoftware/mender-snapshot/vendor/github.com/cpuguy83/go-md2man/v2/LICENSE.md;md5=80794f9009df723bbc6fe19234c9f517 \
    file://src/github.com/mendersoftware/mender-snapshot/vendor/github.com/urfave/cli/v2/LICENSE;md5=51992c80b05795f59c22028d39f9b74c \
    file://src/github.com/mendersoftware/mender-snapshot/vendor/github.com/sirupsen/logrus/LICENSE;md5=8dadfef729c08ec4e631c4f6fc5d43a0 \
    file://src/github.com/mendersoftware/mender-snapshot/vendor/github.com/mattn/go-isatty/LICENSE;md5=f509beadd5a11227c27b5d2ad6c9f2c6 \
    file://src/github.com/mendersoftware/mender-snapshot/vendor/github.com/ungerik/go-sysfs/LICENSE;md5=8dcf593007db59ad07e54ff7908726d2 \
    file://src/github.com/mendersoftware/mender-snapshot/vendor/github.com/stretchr/testify/LICENSE;md5=188f01994659f3c0d310612333d2a26f \
    file://src/github.com/mendersoftware/mender-snapshot/vendor/github.com/creack/pty/LICENSE;md5=93958070863d769117fa33b129020050 \
    file://src/github.com/mendersoftware/mender-snapshot/vendor/github.com/xrash/smetrics/LICENSE;md5=68418a2b5d025376b21bcbd2d9289f22 \
    file://src/github.com/mendersoftware/mender-snapshot/vendor/go.yaml.in/yaml/v3/LICENSE;md5=3c91c17266710e16afdbb2b6d15c761c \
    file://src/github.com/mendersoftware/mender-snapshot/vendor/github.com/russross/blackfriday/v2/LICENSE.txt;md5=ecf8a8a60560c35a862a4a545f2db1b3 \
    file://src/github.com/mendersoftware/mender-snapshot/vendor/github.com/stretchr/testify/internal/spew/LICENSE;md5=c06795ed54b2a35ebeeb543cd3a73e56 \
"
