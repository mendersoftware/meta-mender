DESCRIPTION = "Mender QA tools"
LICENSE = "Apache-2.0"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/Apache-2.0;md5=89aea4e17d99a7cacdbeed46a0096b10"

SRC_URI = "\
        file://common \
        file://mender-qa \
        file://activate-test-image \
        file://deploy-test-image \
        "

MENDER_QA_TOOLS = "\
                activate-test-image \
                deploy-test-image \
                "

do_install() {
    install -d ${D}${bindir}
    install -m 0755 -t ${D}${bindir} ${WORKDIR}/mender-qa

    install -d ${D}${datadir}/mender-qa
    install -m 0644 -t ${D}${datadir}/mender-qa ${WORKDIR}/common

    touch ${D}${datadir}/mender-qa/commands
    for tool in ${MENDER_QA_TOOLS}; do
        install -m 0755 -t ${D}${datadir}/mender-qa ${WORKDIR}/${tool}
        echo ${tool} >> ${D}${datadir}/mender-qa/commands
    done

}

FILES_${PN} = "\
            ${bindir}/* \
            ${datadir}/mender-qa \
            "

RDEPENDS_${PN} = "bash"

# package carries machine specific scripts
PACKAGE_ARCH = "${MACHINE_ARCH}"