require mender-monitor.inc

# REMOVE THIS patch when making a new recipe. All new versions should already
# have licenses included in the package.
FILESEXTRAPATHS:prepend := "${THISDIR}/patches:"
SRC_URI:append = " file://add-missing-licenses.patch"

# DO NOT change the checksum here without make sure that ALL licenses (including
# dependencies) are included in the LICENSE variable below.
LICENSE = "Mender-Yocto-Layer-License.md"
LICENSE_FLAGS = "commercial_mender-yocto-layer-license"
LIC_FILES_CHKSUM = " \
    file://licenses/LICENSE.md;md5=66a40d48ea33620d1bb8d9a4204cde36 \
"

# Enable this in Betas, and in branches that cannot carry this major version as
# default.
# Downprioritize this recipe in version selections.
#DEFAULT_PREFERENCE = "-1"
