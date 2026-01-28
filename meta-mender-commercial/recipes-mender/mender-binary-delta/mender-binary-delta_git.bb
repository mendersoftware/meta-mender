require mender-binary-delta.inc

inherit mender-closed-source-utils

# DO NOT change the checksum here without make sure that ALL licenses (including
# dependencies) are included in the LICENSE variable below.
LICENSE = "Mender-Yocto-Layer-License.md & Apache-2.0"
LICENSE_FLAGS = "commercial_mender-yocto-layer-license"
LIC_FILES_CHKSUM = " \
    file://licenses/LICENSE.md;md5=fd6f2f84e25bc8e0cee29484baf2f0e6 \
    file://licenses/xdelta/xdelta3/LICENSE;md5=cf96fa0d649f7c7b16616d95e7880a73 \
    file://licenses/xdelta/xdelta3/cpp-btree/COPYING;md5=3b83ef96387f14655fc854ddc3c6bd57 \
"

# Disables the need for every dependency to be checked, for easier development.
_MENDER_DISABLE_STRICT_LICENSE_CHECKING = "1"

SRCREV = "${@mender_closed_source_srcrev_from_src_uri(d, '${SRC_URI}', 'mender-binary-delta')}"

PV = "${@mender_closed_source_pv_from_preferred_version(d, '${SRCREV}')}"

def tarball_directory_from_pv(d, pv):
    return pv.split("master-git+")[-1]

# Define S to work both on git sha and "master" tarballs
S = "${WORKDIR}/mender-binary-delta-${@tarball_directory_from_pv(d, '${PV}')}"

# Skip version check
MENDER_DEVMODE = "true"

# Downprioritize this recipe in version selections.
DEFAULT_PREFERENCE = "-1"
