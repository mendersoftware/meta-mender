DESCRIPTION = "Mender artifact information"
HOMEPAGE = "https://mender.io"
LICENSE = "Apache-2.0"
LIC_FILES_CHKSUM = "file://Apache-2.0;md5=89aea4e17d99a7cacdbeed46a0096b10"

FILESPATH = "${COMMON_LICENSE_DIR}"
SRC_URI = "file://Apache-2.0"

S = "${WORKDIR}"

inherit allarch

PV = "0.1"

do_compile() {
    echo "# populate this file with build info" > ${B}/artifact-info
}

do_install() {
    install -d ${D}${sysconfdir}/mender
    install -t ${D}${sysconfdir}/mender ${B}/artifact-info
    ln -s artifact-info ${D}${sysconfdir}/mender/build_mender
}

FILES_${PN} += " \
    ${sysconfdir}/mender/artifact-info \
    ${sysconfdir}/mender/build_mender \
"
