DESCRIPTION = "Mender self-signed server certificate"
HOMEPAGE = "https://mender.io"
LICENSE = "Apache-2.0"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/Apache-2.0;md5=89aea4e17d99a7cacdbeed46a0096b10"

DEPENDS = "ca-certificates"
RDEPENDS_${PN} = "ca-certificates"

S = "${WORKDIR}"
localdatadir = "${prefix}/local/share"

inherit allarch

PV = "0.1"

do_install() {
    if [ ! -f ${WORKDIR}/server.crt ]; then
        bbfatal "No server server.crt found in SRC_URI"
    fi

    install -m 0755 -d ${D}${localdatadir}/ca-certificates/mender
    install -m 0444 ${WORKDIR}/server.crt ${D}${localdatadir}/ca-certificates/mender/server.crt
}

FILES_${PN} += " \
    ${localdatadir}/ca-certificates/mender/server.crt \
"

pkg_postinst_${PN} () {
    SYSROOT="$D" $D${sbindir}/update-ca-certificates
}
