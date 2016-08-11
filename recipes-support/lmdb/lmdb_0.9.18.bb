SUMMARY = "Symas Lightning Memory-Mapped Database (LMDB)"
HOMEPAGE = "http://symas.com/mdb/"
LICENSE = "OLDAP-2.8"
LIC_FILES_CHKSUM = "file://LICENSE;md5=153d07ef052c4a37a8fac23bc6031972"

SRC_URI = "https://github.com/LMDB/lmdb/archive/LMDB_${PV}.tar.gz \
           file://0001-Makefile-fixes-for-OE-build.patch \
           "
SRC_URI[md5sum] = "8b7eeb8a6c30b2763581de455d10441b"
SRC_URI[sha256sum] = "dd35b471d6eea84f48f2feece13d121abf59ef255308b8624a36223ffbdf9989"

inherit autotools-brokensep

S = "${WORKDIR}/lmdb-LMDB_${PV}/libraries/liblmdb"

do_compile() {
    oe_runmake "CC=${CC}"
}

do_install() {
    install -d ${D}${bindir}
    install -d ${D}${libdir}
    install -d ${D}${includedir}
    install -d ${D}${mandir}
    sed -i 's:\$(prefix)/man:${mandir}:' Makefile
    oe_runmake DESTDIR=${D} prefix=${prefix} libdir=${libdir} manprefix=${mandir} install
}

PACKAGES =+ "${PN}-tools"
FILES_${PN}-tools = "${bindir}/mdb_*"
