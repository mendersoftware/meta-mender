GO_IMPORT = "github.com/mendersoftware/mender_common"

inherit go

SRC_URI = "git://git@github.com/mendersoftware/mender_common.git;protocol=ssh"
SRCREV = "${AUTOREV}"

LICENSE = "Apache-2.0"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/Apache-2.0;md5=89aea4e17d99a7cacdbeed46a0096b10"

FILES_${PN} += "${GOBIN_FINAL}/*"


