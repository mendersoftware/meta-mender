LICENSE = "CLOSED"
LICENSE_FLAGS = "commercial"

inherit systemd

RDEPENDS:${PN} = "bash mender-client (>= 2.5) lmdb"

FILES:${PN} = " \
    ${bindir}/mender-monitord \
    ${bindir}/mender-monitorctl \
    ${sysconfdir}/mender-monitor \
    ${datadir}/mender-monitor \
    ${localstatedir}/lib/mender-monitor \
    /data/mender-monitor \
"

FILES:${PN}:append_mender-systemd = " \
    ${systemd_system_unitdir}/mender-monitor.service \
"

S = "${WORKDIR}/mender-monitor"

do_version_check() {
    if ! ${@'true' if d.getVar('MENDER_DEVMODE') else 'false'}; then
        tarball_version=$(cat ${S}/.version)
        if [ "${tarball_version}" != "${PV}" ]; then
            bbfatal "Version '${PV}' not found in .version file from the tarball. Is it the correct version? Found '${tarball_version}'"
        fi
    fi
}
addtask do_version_check after do_unpack before do_install

SYSTEMD_SERVICE:${PN}_mender-systemd = "mender-monitor.service"

do_install() {
    oe_runmake \
        -C ${S} \
        DESTDIR=${D} \
        install
    install -d ${D}/${localstatedir}/lib/mender-monitor
}

do_install:append_mender-systemd() {
    oe_runmake \
        -C ${S} \
        DESTDIR=${D} \
        install-systemd
}

do_install:append_mender-image() {
        # symlink /var/lib/mender-monitor to /data/mender-monitor
        rm -rf ${D}/${localstatedir}/lib/mender-monitor
        ln -s /data/mender-monitor ${D}/${localstatedir}/lib/mender-monitor

        install -m 755 -d ${D}/data/mender-monitor
}

