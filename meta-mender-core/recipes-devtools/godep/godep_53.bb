inherit cross
inherit go

SRC_URI = "git://github.com/tools/godep;protocol=https;destsuffix=godep-${PV}/src/github.com/tools/godep"

SRCREV_pn-godep = "955e36c90cb22b2315f48ab773b653532627d53d"

LICENSE = "BSD-3-Clause"
LIC_FILES_CHKSUM = "file://${S}/src/github.com/tools/godep/License;md5=71eb66e9b353dd06ca5a81ce0f469e1a"

do_compile() {
  GOPATH="${B}:${S}"
  export GOPATH

  # Compile for build architecture.
  CGO_ENABLED=0 GOARCH= go install github.com/tools/godep
}

do_install() {
  install -d "${D}/${bindir}"
  install -m 0755 "${B}/bin/godep" "${D}/${bindir}"
}
