LICENSE = "Apache-2.0"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/${LICENSE};md5=89aea4e17d99a7cacdbeed46a0096b10"

RDEPENDS_${PN} = "python3"

FILESEXTRAPATHS_prepend := "${THISDIR}/files:"
SRC_URI = " \
	file://ab_setup.py \
	"

S = "${WORKDIR}"

do_compile() {
    :
}

do_install() {
	install -d ${D}${sbindir}
	install -m 0755 "${WORKDIR}/ab_setup.py" "${D}${sbindir}"
	ln -s "../..${sbindir}/ab_setup.py" "${D}${sbindir}/fw_printenv"
	ln -s "../..${sbindir}/ab_setup.py" "${D}${sbindir}/fw_setenv"
}

BBCLASSEXTEND += "native"
