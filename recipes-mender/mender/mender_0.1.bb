DESCRIPTION = "mender"
HOMEPAGE = "https://mender.io/"

#From oe-meta-go (https://github.com/mem/oe-meta-go)
DEPENDS = "go-cross"
S = "${WORKDIR}/git"

SRC_URI = "git://git@github.com/mendersoftware/mender.git;protocol=ssh"
SRCREV = "${AUTOREV}"

LICENSE = "Apache-2.0"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/Apache-2.0;md5=89aea4e17d99a7cacdbeed46a0096b10"


inherit go

do_compile() {
  go build -o mender
}

do_install() {
  install -d "${D}/${bindir}"
  install -m 0755 "${S}/mender" "${D}/${bindir}"
}
