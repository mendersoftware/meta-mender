SUMMARY = "Symas Lightning Memory-Mapped Database (LMDB)"
HOMEPAGE = "http://symas.com/mdb/"
LICENSE = "OLDAP-2.8"
LIC_FILES_CHKSUM = "file://LICENSE;md5=153d07ef052c4a37a8fac23bc6031972"

SRC_URI = " \
    https://github.com/LMDB/lmdb/archive/LMDB_${PV}.tar.gz \
    file://0001-Patch-the-main-Makefile.patch \
"
SRC_URI[md5sum] = "0de89730b8f3f5711c2b3a4ba517b648"
SRC_URI[sha256sum] = "49d7b40949f2ced9bc8b23ea6a89e75471a1c9126537a8b268c318a00b84322b"

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
    oe_runmake DESTDIR=${D} prefix=${prefix} libprefix=${libdir} manprefix=${mandir} install
}
