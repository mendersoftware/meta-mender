require mender-client-cpp.inc

################################################################################
#-------------------------------------------------------------------------------
# THINGS TO CONSIDER FOR EACH RELEASE:
# - SRC_URI (particularly "branch")
# - SRCREV
# - DEFAULT_PREFERENCE
#-------------------------------------------------------------------------------

SRC_URI = "gitsm://github.com/mendersoftware/mender;protocol=https;branch=5.0.x"

# Tag: 5.0.0
SRCREV = "47313c6d30db1da2d24ee099b72e0917d2b82254"

# Enable this in Betas, and in branches that cannot carry this major version as
# default.
# Downprioritize this recipe in version selections.
DEFAULT_PREFERENCE = "-1"

################################################################################

# DO NOT change the checksum here without make sure that ALL licenses (including
# dependencies) are included in the LICENSE variable below. Note that for
# releases, we must check the LIC_FILES_CHKSUM.sha256 file, not the LICENSE
# file.
LIC_FILES_CHKSUM = " \
    file://LICENSE;md5=30b4554c64108561c0cb1c57e8a044f0 \
    file://src/common/vendor/yaml-cpp/test/gtest-1.11.0/googlemock/scripts/generator/LICENSE;md5=2c0b90db7465231447cf2dd2e8163333 \
    file://src/common/vendor/json/LICENSE.MIT;md5=67f35caa1c9c8d3d990356bfecf802fb \
    file://src/common/vendor/json/docs/mkdocs/docs/home/license.md;md5=a30fca2d241ce1bc9c268fc2bb7cca74 \
    file://src/common/vendor/tiny-process-library/LICENSE;md5=14d72bb1dc7487cee6c51cedd497eccd \
    file://src/common/vendor/yaml-cpp/LICENSE;md5=6a8aaf0595c2efc1a9c2e0913e9c1a2c \
    file://src/common/vendor/lmdbxx/UNLICENSE;md5=7246f848faa4e9c9fc0ea91122d6e680 \
    file://src/common/vendor/expected/COPYING;md5=65d3616852dbf7b1a6d4b53b00626032 \
    file://src/common/vendor/optional-lite/LICENSE.txt;md5=e4224ccaecb14d942c71d31bef20d78c \
    file://src/common/vendor/yaml-cpp/test/gtest-1.11.0/LICENSE;md5=cbbd27594afd089daa160d3a16dd515a \
"
LICENSE = "Apache-2.0 & BSL-1.0 & CC0-1.0 & MIT & Unlicense"

