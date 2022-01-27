LICENSE = "CLOSED"
LICENSE_FLAGS = "commercial"

inherit systemd

FILES_${PN} = " \
    ${bindir}/mender-gateway \
"

FILES_${PN}_append_mender-systemd = " \
    ${systemd_system_unitdir}/mender-gateway.service \
"

S = "${WORKDIR}/mender-gateway"

do_version_check() {
    if ! ${@'true' if d.getVar('MENDER_DEVMODE') else 'false'}; then
        tarball_version=$(cat ${S}/.version)
        if [ "${tarball_version}" != "${PV}" ]; then
            bbfatal "Version '${PV}' not found in .version file from the tarball. Is it the correct version? Found '${tarball_version}'"
        fi
    fi
}
addtask do_version_check after do_unpack before do_install

SYSTEMD_SERVICE_${PN}_mender-systemd = "mender-gateway.service"

do_install() {
    oe_runmake \
        -C ${S} \
        DESTDIR=${D} \
        install-bin
}

do_install_append_mender-systemd() {
    oe_runmake \
        -C ${S} \
        DESTDIR=${D} \
        install-systemd
}
