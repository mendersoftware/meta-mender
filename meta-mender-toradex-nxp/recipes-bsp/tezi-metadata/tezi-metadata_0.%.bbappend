
FILESEXTRAPATHS_prepend := "${THISDIR}/files:"
SRC_URI_append = " \
    file://prepare.sh;subdir=${PN}-${PV} \
    file://wrapup.sh;subdir=${PN}-${PV} \
    file://mender_toradex_linux.png;subdir=${PN}-${PV} \
    file://marketing_mender_toradex.tar;unpack=false;subdir=${PN}-${PV} \
"

do_deploy_prepend() {
    install -m 644 ${WORKDIR}/${PN}-${PV}/prepare.sh ${DEPLOYDIR}/
    install -m 644 ${WORKDIR}/${PN}-${PV}/wrapup.sh ${DEPLOYDIR}/
    install -m 644 ${WORKDIR}/${PN}-${PV}/mender_toradex_linux.png ${DEPLOYDIR}/
    install -m 644 ${WORKDIR}/${PN}-${PV}/marketing_mender_toradex.tar ${DEPLOYDIR}/
    return 0
}

addtask do_deploy after do_compile
