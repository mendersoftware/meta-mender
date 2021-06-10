LICENSE = "CLOSED"
LICENSE_FLAGS = "commercial"

RDEPENDS_${PN} = "bash mender-client (>= 2.5)"

FILES_${PN} = " \
    ${bindir}/monitord \
    ${sysconfdir}/monitor \
    ${datadir}/monitor \
"

S = "${WORKDIR}/${PN}"

do_version_check() {
    if ! ${@'true' if d.getVar('MENDER_DEVMODE') else 'false'}; then
        tarball_version=$(cat ${S}/.version)
        if [ "${tarball_version}" != "${PV}" ]; then
            bbfatal "Version '${PV}' not found in .version file from the tarball. Is it the correct version? Found '${tarball_version}'"
        fi
    fi
}
addtask do_version_check after do_unpack before do_install

do_install() {
    oe_runmake \
        -C ${S} \
        DESTDIR=${D} \
        install
}
