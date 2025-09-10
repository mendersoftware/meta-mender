inherit mender-licensing

DESCRIPTION = "Interfaces and Update Modules for mender-orchestrator"

RDEPENDS:${PN} = "mender-orchestrator"

FILES:${PN} = " \
    ${datadir}/mender-orchestrator/interfaces/v1/rootfs-image \
    ${datadir}/mender/modules/v3/mender-orchestrator-manifest \
"

S = "${WORKDIR}/git"

do_install() {
    # Install interfaces using the Makefile
    oe_runmake \
        -C ${S} \
        DESTDIR=${D} \
        prefix=${D} \
        install

    # Manually install the orchestrator-manifest module
    install -d -m 755 ${D}${datadir}/mender/modules/v3/
    install -m 755 ${S}/modules/mender-orchestrator-manifest/module/v3/mender-orchestrator-manifest \
        ${D}${datadir}/mender/modules/v3/
}
