require mender-client-cpp.inc
require mender_4.x.inc

################################################################################
#-------------------------------------------------------------------------------
# THINGS TO CONSIDER FOR EACH RELEASE:
# - SRC_URI (particularly "branch")
# - SRCREV
# - DEFAULT_PREFERENCE
#-------------------------------------------------------------------------------

SRC_URI = "gitsm://github.com/mendersoftware/mender;protocol=https;branch=4.0.x"

# Tag: 4.0.4
SRCREV = "80f37fe47f9eac22d78a8a848b77072d45976c3e"

# Enable this in Betas, and in branches that cannot carry this major version as
# default.
# Downprioritize this recipe in version selections.
#DEFAULT_PREFERENCE = "-1"

################################################################################

# DO NOT change the checksum here without make sure that ALL licenses (including
# dependencies) are included in the LICENSE variable below. Note that for
# releases, we must check the LIC_FILES_CHKSUM.sha256 file, not the LICENSE
# file.
LIC_FILES_CHKSUM = " \
    file://LICENSE;md5=30b4554c64108561c0cb1c57e8a044f0 \
    file://vendor/json/LICENSE.MIT;md5=f969127d7b7ed0a8a63c2bbeae002588 \
    file://vendor/json/docs/mkdocs/docs/home/license.md;md5=970ea048f6ea7d04eeb3ba3ef9ebca40 \
    file://vendor/tiny-process-library/LICENSE;md5=14d72bb1dc7487cee6c51cedd497eccd \
    file://vendor/lmdbxx/UNLICENSE;md5=7246f848faa4e9c9fc0ea91122d6e680 \
    file://vendor/expected/COPYING;md5=65d3616852dbf7b1a6d4b53b00626032 \
    file://vendor/optional-lite/LICENSE.txt;md5=e4224ccaecb14d942c71d31bef20d78c \
"
LICENSE = "Apache-2.0 & BSL-1.0 & CC0-1.0 & MIT & Unlicense"

