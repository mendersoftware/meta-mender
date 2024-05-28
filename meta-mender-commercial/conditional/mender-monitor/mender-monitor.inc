inherit mender-licensing

inherit systemd

RDEPENDS:${PN} = "bash mender-auth lmdb coreutils"


FILES:${PN} = " \
    ${bindir}/mender-monitord \
    ${bindir}/mender-monitorctl \
    ${sysconfdir}/mender-monitor \
    ${datadir}/mender-monitor \
    ${localstatedir}/lib/mender-monitor \
    /data/mender-monitor \
"

FILES:${PN}:append:mender-systemd = " \
    ${systemd_system_unitdir}/mender-monitor.service \
"

S = "${WORKDIR}/mender-monitor"

do_version_check() {
    if [ ! -e ${S}/.version ]; then
        bbfatal "No mender-monitor files found. Have you added the package to SRC_URI?"
    fi

    if ! ${@'true' if d.getVar('MENDER_DEVMODE') else 'false'}; then
        tarball_version=$(cat ${S}/.version)
        if [ "${tarball_version}" != "${PV}" ]; then
            bbfatal "Version '${PV}' not found in .version file from the tarball. Is it the correct version? Found '${tarball_version}'"
        fi
    fi
}
addtask do_version_check after do_unpack before do_install

SYSTEMD_SERVICE:${PN}:mender-systemd = "mender-monitor.service"

do_install() {
    oe_runmake \
        -C ${S} \
        DESTDIR=${D} \
        install
    install -d ${D}/${localstatedir}/lib/mender-monitor
}

do_install:append:mender-systemd() {
    oe_runmake \
        -C ${S} \
        DESTDIR=${D} \
        install-systemd
}

do_install:append:mender-image() {
        # symlink /var/lib/mender-monitor to /data/mender-monitor
        rm -rf ${D}/${localstatedir}/lib/mender-monitor
        ln -s /data/mender-monitor ${D}/${localstatedir}/lib/mender-monitor

        install -m 755 -d ${D}/data/mender-monitor
}
