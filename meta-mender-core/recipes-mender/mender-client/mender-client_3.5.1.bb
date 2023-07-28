require mender-client.inc

################################################################################
#-------------------------------------------------------------------------------
# THINGS TO CONSIDER FOR EACH RELEASE:
# - SRC_URI (particularly "branch")
# - SRCREV
# - DEFAULT_PREFERENCE
#-------------------------------------------------------------------------------

SRC_URI = "git://github.com/mendersoftware/mender;protocol=https;branch=3.5.x"

# Tag: 3.5.1
SRCREV = "e48c2fc825ad0c273d19f3ce00eec867091a0806"

# Enable this in Betas, and in branches that cannot carry this major version as
# default.
# Downprioritize this recipe in version selections.
# DEFAULT_PREFERENCE = "-1"

################################################################################

# DO NOT change the checksum here without make sure that ALL licenses (including
# dependencies) are included in the LICENSE variable below. Note that for
# releases, we must check the LIC_FILES_CHKSUM.sha256 file, not the LICENSE
# file.
LIC_FILES_CHKSUM = " \
    file://src/github.com/mendersoftware/mender/LICENSE;md5=b4b4cfdaea6d61aa5793b92efd42e081 \
    file://src/github.com/mendersoftware/mender/vendor/github.com/mendersoftware/mender-artifact/LICENSE;md5=b4b4cfdaea6d61aa5793b92efd42e081 \
    file://src/github.com/mendersoftware/mender/vendor/github.com/mendersoftware/openssl/LICENSE;md5=19cbd64715b51267a47bf3750cc6a8a5 \
    file://src/github.com/mendersoftware/mender/vendor/github.com/minio/sha256-simd/LICENSE;md5=3b83ef96387f14655fc854ddc3c6bd57 \
    file://src/github.com/mendersoftware/mender/vendor/github.com/mendersoftware/progressbar/LICENSE;md5=dcac2e5bf81a6fe99b034aaaaf1b2019 \
    file://src/github.com/mendersoftware/mender/vendor/github.com/pkg/errors/LICENSE;md5=6fe682a02df52c6653f33bd0f7126b5a \
    file://src/github.com/mendersoftware/mender/vendor/github.com/godbus/dbus/LICENSE;md5=09042bd5c6c96a2b9e45ddf1bc517eed \
    file://src/github.com/mendersoftware/mender/vendor/github.com/gorilla/websocket/LICENSE;md5=c007b54a1743d596f46b2748d9f8c044 \
    file://src/github.com/mendersoftware/mender/vendor/github.com/klauspost/compress/LICENSE;md5=d0fd9ebda39468b51ff4539c9fbb13a8 \
    file://src/github.com/mendersoftware/mender/vendor/github.com/pmezard/go-difflib/LICENSE;md5=e9a2ebb8de779a07500ddecca806145e \
    file://src/github.com/mendersoftware/mender/vendor/golang.org/x/sys/LICENSE;md5=5d4950ecb7b26d2c5e4e7b4e0dd74707 \
    file://src/github.com/mendersoftware/mender/vendor/github.com/bmatsuo/lmdb-go/LICENSE.md;md5=4735f81f41df64865d24bf38e42595da \
    file://src/github.com/mendersoftware/mender/vendor/github.com/remyoudompheng/go-liblzma/LICENSE;md5=344ad0e1a666fa2b8eccea6b1b742e42 \
    file://src/github.com/mendersoftware/mender/vendor/golang.org/x/term/LICENSE;md5=5d4950ecb7b26d2c5e4e7b4e0dd74707 \
    file://src/github.com/mendersoftware/mender/vendor/github.com/davecgh/go-spew/LICENSE;md5=c06795ed54b2a35ebeeb543cd3a73e56 \
    file://src/github.com/mendersoftware/mender/vendor/github.com/klauspost/pgzip/LICENSE;md5=a6862811c790a468c5d82d68e717c154 \
    file://src/github.com/mendersoftware/mender/vendor/github.com/klauspost/compress/internal/snapref/LICENSE;md5=b8b79c7d4cda128290b98c6a21f9aac6 \
    file://src/github.com/mendersoftware/mender/vendor/github.com/klauspost/compress/zstd/internal/xxhash/LICENSE.txt;md5=802da049c92a99b4387d3f3d91b00fa9 \
    file://src/github.com/mendersoftware/mender/vendor/github.com/klauspost/cpuid/v2/LICENSE;md5=00d6f962401947482d082858f7ba2ff3 \
    file://src/github.com/mendersoftware/mender/vendor/github.com/sirupsen/logrus/LICENSE;md5=8dadfef729c08ec4e631c4f6fc5d43a0 \
    file://src/github.com/mendersoftware/mender/vendor/github.com/stretchr/testify/LICENSE;md5=188f01994659f3c0d310612333d2a26f \
    file://src/github.com/mendersoftware/mender/vendor/github.com/ungerik/go-sysfs/LICENSE;md5=8dcf593007db59ad07e54ff7908726d2 \
    file://src/github.com/mendersoftware/mender/vendor/github.com/urfave/cli/v2/LICENSE;md5=c542707ca9fc0b7802407ba62310bd8f \
    file://src/github.com/mendersoftware/mender/vendor/github.com/stretchr/objx/LICENSE;md5=d023fd31d3ca39ec61eec65a91732735 \
    file://src/github.com/mendersoftware/mender/vendor/gopkg.in/yaml.v3/LICENSE;md5=3c91c17266710e16afdbb2b6d15c761c \
    file://src/github.com/mendersoftware/mender/vendor/github.com/mattn/go-isatty/LICENSE;md5=f509beadd5a11227c27b5d2ad6c9f2c6 \
    file://src/github.com/mendersoftware/mender/vendor/github.com/bmatsuo/lmdb-go/LICENSE.mdb.md;md5=153d07ef052c4a37a8fac23bc6031972 \
"
LICENSE = "Apache-2.0 & BSD-2-Clause & BSD-3-Clause & ISC & MIT & OLDAP-2.8"

DEPENDS = "xz openssl"
RDEPENDS:${PN} = "liblzma openssl"
