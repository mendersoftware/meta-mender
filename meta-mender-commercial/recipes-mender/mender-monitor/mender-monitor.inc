LICENSE = "CLOSED"
LICENSE_FLAGS = "commercial"

inherit systemd

RDEPENDS_${PN} = "bash mender-client (>= 2.5)"

FILES_${PN} = " \
    ${bindir}/mender-monitord \
    ${bindir}/mender-monitorctl \
    ${sysconfdir}/mender-monitor \
    ${datadir}/mender-monitor \
    ${localstatedir}/lib/mender-monitor \
    /data/mender-monitor \
"

FILES_${PN}_append_mender-systemd = " \
    ${systemd_system_unitdir}/mender-monitor.service \
"

S ?= "${WORKDIR}/${PN}"

do_version_check() {
    if ! ${@'true' if d.getVar('MENDER_DEVMODE') else 'false'}; then
        bbfatal "Not yet released. This recipe can only be used with MENDER_DEVMODE"
    fi
}
addtask do_version_check after do_unpack before do_install

SYSTEMD_SERVICE_${PN}_mender-systemd = "mender-monitor.service"

do_install() {
    oe_runmake \
        -C ${S} \
        DESTDIR=${D} \
        install
    install -d ${D}/${localstatedir}/lib/mender-monitor
}

do_install_append_mender-systemd() {
    oe_runmake \
        -C ${S} \
        DESTDIR=${D} \
        install-systemd
}

do_install_append_mender-image() {
        # symlink /var/lib/mender-monitor to /data/mender-monitor
        rm -rf ${D}/${localstatedir}/lib/mender-monitor
        ln -s /data/mender-monitor ${D}/${localstatedir}/lib/mender-monitor

        install -m 755 -d ${D}/data/mender-monitor
}

