# Check if mender-orchestrator recipe already includes topology.yaml in its SRC_URI
HAS_TOPOLOGY = "${@'true' if 'topology.yaml' in (d.getVar('SRC_URI:pn-mender-orchestrator') or '') else 'false'}"

FILES:${PN} += " \
    /data/mender-orchestrator/mock-instances \
    ${datadir}/mender-orchestrator/interfaces/v1/rtos \
    ${@'' if d.getVar('HAS_TOPOLOGY') == 'true' else ' /data/mender-orchestrator/topology.yaml'} \
"

do_install:append() {
    # Install mock instances and interfaces
    oe_runmake -C ${S} prefix=${D} install-mock-instances
    oe_runmake -C ${S} prefix=${D} install-mock-interfaces

    # Only install mock topology if mender-orchestrator doesn't provide one
    if [ "${HAS_TOPOLOGY}" != "true" ]; then
        oe_runmake -C ${S} prefix=${D} install-mock-topology
    fi
}
