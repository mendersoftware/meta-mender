require mender-gateway.inc

inherit mender-closed-source-utils

# DO NOT change the checksum here without make sure that ALL licenses (including
# dependencies) are included in the LICENSE variable below.
LICENSE = "Mender-Yocto-Layer-License.md & Apache-2.0 & BSD-2-Clause & BSD-3-Clause & ISC & MIT"
LICENSE_FLAGS = "commercial_mender-yocto-layer-license"
LIC_FILES_CHKSUM = " \
    file://licenses/LICENSE.md;md5=ddb0c461e9cc224aa6aff51b108f26b8 \
"

# Disables the need for every dependency to be checked, for easier development.
_MENDER_DISABLE_STRICT_LICENSE_CHECKING = "1"

SRCREV = "${@mender_closed_source_srcrev_from_src_uri(d, '${SRC_URI}', 'mender-gateway')}"

PV = "${@mender_closed_source_pv_from_preferred_version(d, '${SRCREV}')}"

def tarball_directory_from_pv(d, pv):
    return pv.split("master-git+")[-1]

# Define S to work both on git sha and "master" tarballs
S = "${WORKDIR}/mender-gateway-${@tarball_directory_from_pv(d, '${PV}')}"

# Skip version check
MENDER_DEVMODE = "true"

# Downprioritize this recipe in version selections.
DEFAULT_PREFERENCE = "-1"
