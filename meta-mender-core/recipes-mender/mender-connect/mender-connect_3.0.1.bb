require mender-connect.inc

################################################################################
#-------------------------------------------------------------------------------
# THINGS TO CONSIDER FOR EACH RELEASE:
# - SRC_URI (particularly "branch")
# - SRCREV
# - DEFAULT_PREFERENCE
#-------------------------------------------------------------------------------

SRC_URI = "git://github.com/mendersoftware/mender-connect.git;protocol=https;destsuffix=${GO_SRCURI_DESTSUFFIX};branch=3.0.x"

# Tag: 3.0.1
SRCREV = "6191b612e03ba6878c4573cc9a8d8e866057cdad"

# Enable this in Betas, and in branches that cannot carry this major version as
# default.
# Downprioritize this recipe in version selections.
# DEFAULT_PREFERENCE = "-1"

################################################################################

# DO NOT change the checksum here without make sure that ALL licenses (including
# dependencies) are included in the LICENSE variable below. Note that for
# releases, we must check the LIC_FILES_CHKSUM.sha256 file, not the LICENSE
# file.
LICENSE = "Apache-2.0 & BSD-2-Clause & BSD-3-Clause & ISC & MIT"
LIC_FILES_CHKSUM = " \
    file://src/github.com/mendersoftware/mender-connect/LICENSE;md5=a8c81350f12516cbb62844f937d81d11 \
    file://src/github.com/mendersoftware/mender-connect/vendor/github.com/mendersoftware/go-lib-micro/LICENSE;md5=b633dec416a3d32c67acb1f332964580 \
    file://src/github.com/mendersoftware/mender-connect/vendor/github.com/pkg/errors/LICENSE;md5=6fe682a02df52c6653f33bd0f7126b5a \
    file://src/github.com/mendersoftware/mender-connect/vendor/github.com/russross/blackfriday/v2/LICENSE.txt;md5=ecf8a8a60560c35a862a4a545f2db1b3 \
    file://src/github.com/mendersoftware/mender-connect/vendor/github.com/vmihailenco/msgpack/v5/LICENSE;md5=5de50b60705d666cd9542dd48d5e4b56 \
    file://src/github.com/mendersoftware/mender-connect/vendor/github.com/vmihailenco/tagparser/v2/LICENSE;md5=e9f573ea1e3d968278166de82cd36301 \
    file://src/github.com/mendersoftware/mender-connect/vendor/github.com/stretchr/testify/internal/difflib/LICENSE;md5=37bee94299cc4febcbc4c52da854074d \
    file://src/github.com/mendersoftware/mender-connect/vendor/golang.org/x/sys/LICENSE;md5=7998cb338f82d15c0eff93b7004d272a \
    file://src/github.com/mendersoftware/mender-connect/vendor/github.com/gorilla/websocket/LICENSE;md5=c007b54a1743d596f46b2748d9f8c044 \
    file://src/github.com/mendersoftware/mender-connect/vendor/github.com/stretchr/testify/internal/spew/LICENSE;md5=c06795ed54b2a35ebeeb543cd3a73e56 \
    file://src/github.com/mendersoftware/mender-connect/vendor/github.com/cpuguy83/go-md2man/v2/LICENSE.md;md5=80794f9009df723bbc6fe19234c9f517 \
    file://src/github.com/mendersoftware/mender-connect/vendor/github.com/creack/pty/LICENSE;md5=93958070863d769117fa33b129020050 \
    file://src/github.com/mendersoftware/mender-connect/vendor/github.com/go-ozzo/ozzo-validation/v4/LICENSE;md5=da12d993f2ce14947ad6eec35520b081 \
    file://src/github.com/mendersoftware/mender-connect/vendor/github.com/satori/go.uuid/LICENSE;md5=ae4ba217c6e20c2d8f48f69966b9121b \
    file://src/github.com/mendersoftware/mender-connect/vendor/github.com/shurcooL/sanitized_anchor_name/LICENSE;md5=c670c44b8d826e9b7b99077e5c7ba283 \
    file://src/github.com/mendersoftware/mender-connect/vendor/github.com/sirupsen/logrus/LICENSE;md5=8dadfef729c08ec4e631c4f6fc5d43a0 \
    file://src/github.com/mendersoftware/mender-connect/vendor/github.com/stretchr/objx/LICENSE;md5=d023fd31d3ca39ec61eec65a91732735 \
    file://src/github.com/mendersoftware/mender-connect/vendor/github.com/stretchr/testify/LICENSE;md5=188f01994659f3c0d310612333d2a26f \
    file://src/github.com/mendersoftware/mender-connect/vendor/github.com/urfave/cli/v2/LICENSE;md5=c542707ca9fc0b7802407ba62310bd8f \
    file://src/github.com/mendersoftware/mender-connect/vendor/go.yaml.in/yaml/v3/LICENSE;md5=3c91c17266710e16afdbb2b6d15c761c \
"
