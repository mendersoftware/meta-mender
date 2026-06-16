inherit mender-licensing

DESCRIPTION = "Interfaces and Update Modules for mender-orchestrator"

RDEPENDS:${PN} = "mender-orchestrator"

FILES:${PN} = " \
    ${datadir}/mender-orchestrator/interfaces/v1/rootfs-image \
"

FILES:${PN}:append:mender-update-install = " \
    ${datadir}/mender/modules/v3/mender-orchestrator-manifest \
    ${datadir}/mender/inventory/mender-inventory-mender-orchestrator \
"

do_install() {
    # Install interfaces using the Makefile
    oe_runmake \
        -C ${S} \
        DESTDIR=${D} \
        prefix=${D} \
        install
}

do_install:append:mender-update-install() {
    # Manually install the orchestrator-manifest module
    install -d -m 755 ${D}${datadir}/mender/modules/v3/
    install -m 755 ${S}/modules/mender-orchestrator-manifest/module/v3/mender-orchestrator-manifest \
        ${D}${datadir}/mender/modules/v3/

    # Install the inventory script
    install -d -m 755 ${D}${datadir}/mender/inventory/
    install -m 755 ${S}/inventory/mender-inventory-mender-orchestrator ${D}${datadir}/mender/inventory/mender-inventory-mender-orchestrator
}
