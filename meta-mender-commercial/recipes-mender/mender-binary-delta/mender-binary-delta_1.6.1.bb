require mender-binary-delta.inc

# DO NOT change the checksum here without make sure that ALL licenses (including
# dependencies) are included in the LICENSE variable below.
LICENSE = "Mender-Yocto-Layer-License.md & Apache-2.0"
LICENSE_FLAGS = "commercial_mender-yocto-layer-license"
LIC_FILES_CHKSUM = " \
    file://licenses/LICENSE.md;md5=fd6f2f84e25bc8e0cee29484baf2f0e6 \
    file://licenses/xdelta/xdelta3/LICENSE;md5=cf96fa0d649f7c7b16616d95e7880a73 \
    file://licenses/libntech/LICENSE;md5=07c4fb9c7586a0e38a6891cb096a726b \
    file://licenses/xdelta/xdelta1/COPYING;md5=8ca43cbc842c2336e835926c2166c28b \
"

# Enable this in Betas, and in branches that cannot carry this major version as
# default.
# Downprioritize this recipe in version selections.
# DEFAULT_PREFERENCE = "-1"
