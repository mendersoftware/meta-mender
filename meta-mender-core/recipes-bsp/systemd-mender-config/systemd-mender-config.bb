LICENSE = "Apache-2.0"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/${LICENSE};md5=89aea4e17d99a7cacdbeed46a0096b10"

RDEPENDS:${PN} = "python3"

FILESEXTRAPATHS:prepend := "${THISDIR}/files:"
SRC_URI = " \
    file://ab_setup.py \
    "

S = "${WORKDIR}"

FILES:${PN}:append = "\
    /mnt/inactive \
"

do_compile() {
    :
}

do_install() {
    install -d ${D}${sbindir}
    install -d ${D}/mnt/inactive
    install -m 0755 "${WORKDIR}/ab_setup.py" "${D}${sbindir}"

    ln -s "../..${sbindir}/ab_setup.py" "${D}${sbindir}/systemd-boot-printenv"
    ln -s "../..${sbindir}/ab_setup.py" "${D}${sbindir}/systemd-boot-setenv"
    ln -s "../..${sbindir}/ab_setup.py" "${D}${sbindir}/fw_printenv"
    ln -s "../..${sbindir}/ab_setup.py" "${D}${sbindir}/fw_setenv"
}

BBCLASSEXTEND += "native"
