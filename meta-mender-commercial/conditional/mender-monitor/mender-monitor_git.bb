require mender-monitor.inc

inherit mender-closed-source-utils

# DO NOT change the checksum here without make sure that ALL licenses (including
# dependencies) are included in the LICENSE variable below.
LICENSE = "Mender-Yocto-Layer-License.md"
LICENSE_FLAGS = "commercial_mender-yocto-layer-license"
LIC_FILES_CHKSUM = " \
    file://licenses/LICENSE.md;md5=ddb0c461e9cc224aa6aff51b108f26b8 \
"

# Disables the need for every dependency to be checked, for easier development.
_MENDER_DISABLE_STRICT_LICENSE_CHECKING = "1"

SRCREV = "${@mender_closed_source_srcrev_from_src_uri(d, '${SRC_URI}', 'mender-monitor')}"

PV = "${@mender_closed_source_pv_from_preferred_version(d, '${SRCREV}')}"

# Skip version check
MENDER_DEVMODE = "true"

# Downprioritize this recipe in version selections.
DEFAULT_PREFERENCE = "-1"
