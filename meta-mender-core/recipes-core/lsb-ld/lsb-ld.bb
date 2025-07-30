SUMMARY = "Absolute minimum LSB support to enable /lib64 directory"
LICENSE = "Apache-2.0"
LIC_FILES_CHKSUM = "file://LICENSE;md5=269720c1a5608250abd54a7818f369f6"

FILESEXTRAPATHS:append := ":${THISDIR}/files"
SRC_URI = "file://LICENSE"
S = "${WORKDIR}/sources"
UNPACKDIR = "${S}"

# Only x86-64 needs any files.
ALLOW_EMPTY:${PN} = "1"

FILES:${PN}:x86-64 = "/lib64"

do_install:x86-64() {
    # Avoid issues with ./lib64/*.a on multilib systems
    if ${@bb.utils.contains('MULTILIBS','multilib:lib32','false','true',d)}; then
        ln -sf lib ${D}/lib64
    fi
}
