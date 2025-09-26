FILES:${PN} += " \
    /data/mender-orchestrator/mock-instances \
    ${datadir}/mender-orchestrator/interfaces/v1/rtos \
"

python () {
    if bb.utils.which(d.getVar('FILESPATH'), 'topology.yaml', history=False):
        return
    d.setVar('INSTALL_DEMO_TOPOLOGY', 'true')
    d.appendVar('FILES:' + d.getVar('PN'), ' /data/mender-orchestrator/topology.yaml')
}

do_install:append() {
    oe_runmake -C ${S} prefix=${D} install-mock-instances install-mock-interfaces
    if [ "${INSTALL_DEMO_TOPOLOGY}" = "true" ]; then
        oe_runmake -C ${S} prefix=${D} install-mock-topology
    fi
}
