DESCRIPTION = "Mender tool for doing OTA software updates."
HOMEPAGE = "https://mender.io/"

#From oe-meta-go (https://github.com/mem/oe-meta-go)
DEPENDS = "go-cross godep"
S = "${WORKDIR}/git"

inherit go

SRC_URI = "git://github.com/mendersoftware/mender;protocol=https"
SRCREV = "${AUTOREV}"

LICENSE = "Apache-2.0"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/Apache-2.0;md5=89aea4e17d99a7cacdbeed46a0096b10"


do_compile() {
  GOPATH="${B}:${S}"
  export GOPATH
  PATH="${B}/bin:$PATH"
  export PATH

  cd "${S}"
  godep go build -o "${B}/mender"
}

do_install() {
  install -d "${D}/${bindir}"
  install -m 0755 "${B}/mender" "${D}/${bindir}"
}
