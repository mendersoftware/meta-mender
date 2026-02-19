require mender-orchestrator.inc

inherit mender-closed-source-utils

# DO NOT change the checksum here without making sure that ALL licenses (including
# dependencies) are included in the LICENSE variable below.
LICENSE = "Mender-Yocto-Layer-License.md & Apache-2.0 & MIT & CC0-1.0 & BSL-1.0 & BSD-3-Clause"
LICENSE_FLAGS = "commercial_mender-yocto-layer-license"
LIC_FILES_CHKSUM = " \
    file://licenses/LICENSE;md5=425e73757010d92651a87c6338ebce7c \
"

# Disables the need for every dependency to be checked, for easier development.
_MENDER_DISABLE_STRICT_LICENSE_CHECKING = "1"

SRCREV = "${@mender_closed_source_srcrev_from_src_uri(d, '${SRC_URI}', 'mender-orchestrator')}"

PV = "${@mender_closed_source_pv_from_preferred_version(d, '${SRCREV}')}"

def tarball_directory_from_pv(d, pv):
    return pv.split("main-git+")[-1]

# Define S to work both on git sha and "master" tarballs
S = "${WORKDIR}/mender-orchestrator-${@tarball_directory_from_pv(d, '${PV}')}"

# Skip version check
MENDER_DEVMODE = "true"

# Downprioritize this recipe in version selections.
DEFAULT_PREFERENCE = "-1"
