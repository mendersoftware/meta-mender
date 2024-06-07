require mender-binary-delta.inc

# DO NOT change the checksum here without make sure that ALL licenses (including
# dependencies) are included in the LICENSE variable below.
LICENSE = "Mender-Yocto-Layer-License.md & Apache-2.0"
LICENSE_FLAGS = "commercial_mender-yocto-layer-license"
LIC_FILES_CHKSUM = " \
    file://licenses/LICENSE.md;md5=ddb0c461e9cc224aa6aff51b108f26b8 \
    file://licenses/xdelta/xdelta3/LICENSE;md5=cf96fa0d649f7c7b16616d95e7880a73 \
    file://licenses/xdelta/xdelta3/cpp-btree/COPYING;md5=3b83ef96387f14655fc854ddc3c6bd57 \
"

# Enable this in Betas, and in branches that cannot carry this major version as
# default.
# Downprioritize this recipe in version selections.
# DEFAULT_PREFERENCE = "-1"
