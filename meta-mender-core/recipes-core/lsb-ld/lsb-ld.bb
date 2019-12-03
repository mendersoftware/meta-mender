SUMMARY = "Absolute minimum LSB support to enable /lib64 directory"
LICENSE = "Apache-2.0"
LIC_FILES_CHKSUM = "file://LICENSE;md5=269720c1a5608250abd54a7818f369f6"

FILESEXTRAPATHS_append := ":${THISDIR}/files"
SRC_URI = "file://LICENSE"
S = "${WORKDIR}"

# Only x86-64 needs any files.
ALLOW_EMPTY_${PN} = "1"

FILES_${PN}_x86-64 = "/lib64"

do_install_x86-64() {
    ln -sf lib ${D}/lib64
}
