require mender-binary-delta.inc

SRC_URI_arm = "file://${SUB_FOLDER}/mender-binary-delta;subdir=${BP}"
SRC_URI_aarch64 = "file://${SUB_FOLDER}/mender-binary-delta;subdir=${BP}"
SRC_URI_x86-64 = "file://${SUB_FOLDER}/mender-binary-delta;subdir=${BP}"

# REMOVE THIS patch when making a new recipe. All new versions should already
# have licenses included in the package.
FILESEXTRAPATHS_prepend := "${THISDIR}/patches:"
SRC_URI_append = " file://add-missing-licenses.patch"

# DO NOT change the checksum here without make sure that ALL licenses (including
# dependencies) are included in the LICENSE variable below.
LICENSE = "Mender-Yocto-Layer-License.md & Apache-2.0"
LICENSE_FLAGS = "commercial_mender-yocto-layer-license"
LIC_FILES_CHKSUM = " \
    file://licenses/LICENSE.md;md5=66a40d48ea33620d1bb8d9a4204cde36 \
    file://licenses/xdelta/xdelta3/LICENSE;md5=cf96fa0d649f7c7b16616d95e7880a73 \
    file://licenses/xdelta/xdelta3/cpp-btree/COPYING;md5=3b83ef96387f14655fc854ddc3c6bd57 \
"

# Enable this in Betas, and in branches that cannot carry this major version as
# default.
# Downprioritize this recipe in version selections.
#DEFAULT_PREFERENCE = "-1"
