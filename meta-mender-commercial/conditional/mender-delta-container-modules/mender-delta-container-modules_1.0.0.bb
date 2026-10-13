require mender-delta-container-modules.inc

# DO NOT change the checksum here without making sure that ALL licenses (including
# dependencies) are included in the LICENSE variable below.
LICENSE = "Mender-Yocto-Layer-License.md & Apache-2.0"
LICENSE_FLAGS = "commercial_mender-yocto-layer-license"
LIC_FILES_CHKSUM = " \
    file://licenses/LICENSE;md5=fd6f2f84e25bc8e0cee29484baf2f0e6 \
    file://licenses/mender-container-modules/LICENSE;md5=a8c81350f12516cbb62844f937d81d11 \
"

# Enable this in Betas, and in branches that cannot carry this major version as
# default.
# Downprioritize this recipe in version selections.
# DEFAULT_PREFERENCE = "-1"
