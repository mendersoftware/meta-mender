inherit systemd

FILES:${PN} += " \
    /data/mender-orchestrator/mock-instances \
    ${datadir}/mender-orchestrator/interfaces/v1/rtos-interface \
    ${datadir}/mender-orchestrator/interfaces/v1/esp32 \
    ${datadir}/mender-orchestrator/interfaces/v1/mqtt-component \
    /etc/mosquitto/conf.d/mender-orchestrator.conf \
    ${datadir}/mender-orchestrator/remote-mqtt/mender-mqtt-agent \
    /etc/mender-mqtt-agent/mender-mqtt-agent.conf.example \
    /lib/systemd/system/mender-mqtt-agent.service \
"

# mender-mqtt-agent.service is only meaningful on a Component board, only once
# /etc/mender-mqtt-agent/mender-mqtt-agent.conf has been created from the .conf.example (a
# manual step -- see remote-mqtt/README.md), and this same bbappend/package also lands on
# the System Device. Ship the unit but don't auto-enable/start it, matching the equivalent
# fix in mender-dist-packages' debian/rules (dh_systemd_enable/start --no-enable/--no-start).
SYSTEMD_SERVICE:${PN} = "${@'mender-mqtt-agent.service' if os.path.exists(d.getVar('S') + '/remote-mqtt') else ''}"
SYSTEMD_AUTO_ENABLE:${PN} = "disable"

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
    # This bbappend (mender-orchestrator-support_%.bbappend) applies to EVERY version of the
    # recipe -- 0.4.0, 0.5.0, 0.6.0, git, and any future one.
    # install-mqtt-broker/install-mqtt-component-agent only exist in the Makefile starting with
    # 0.7.0; call this conditionally on remote-mqtt existing, to avoid oe_runmake error.
    if [ -d "${S}/remote-mqtt" ]; then
        oe_runmake -C ${S} prefix=${D} install-mqtt-broker install-mqtt-component-agent
    fi
}
