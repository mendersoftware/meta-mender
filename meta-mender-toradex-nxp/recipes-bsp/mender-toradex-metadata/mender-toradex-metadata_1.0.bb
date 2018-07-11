DESCRIPTION = "Toradex Easy Installer Metadata"

inherit deploy

SRC_URI = " \
    file://LICENSE;subdir=${PN}-${PV} \
    file://prepare.sh;subdir=${PN}-${PV} \
    file://wrapup.sh;subdir=${PN}-${PV} \
    file://mender_toradex_linux.png;subdir=${PN}-${PV} \
    file://marketing_mender_toradex.tar;unpack=false;subdir=${PN}-${PV} \
"

LICENSE = "Apache-2.0"
LIC_FILES_CHKSUM = "file://LICENSE;md5=e3fc50a88d0a364313df4b21ef20c29e"

do_deploy() {
    install -d ${DEPLOYDIR}/toradex-easyinstaller
    install -m 644 ${WORKDIR}/${PN}-${PV}/prepare.sh ${DEPLOYDIR}/toradex-easyinstaller/
    install -m 644 ${WORKDIR}/${PN}-${PV}/wrapup.sh ${DEPLOYDIR}/toradex-easyinstaller/
    install -m 644 ${WORKDIR}/${PN}-${PV}/mender_toradex_linux.png ${DEPLOYDIR}/toradex-easyinstaller/
    install -m 644 ${WORKDIR}/${PN}-${PV}/marketing_mender_toradex.tar ${DEPLOYDIR}/toradex-easyinstaller/
}

addtask do_deploy after do_compile

