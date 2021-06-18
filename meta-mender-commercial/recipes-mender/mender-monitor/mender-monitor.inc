LICENSE = "CLOSED"
LICENSE_FLAGS = "commercial"

RDEPENDS_${PN} = "bash mender-client (>= 2.5)"

FILES_${PN} = " \
    ${bindir}/mender-monitord \
    ${sysconfdir}/mender-monitor \
    ${datadir}/mender-monitor \
"

S ?= "${WORKDIR}/${PN}"

do_version_check() {
    if ! ${@'true' if d.getVar('MENDER_DEVMODE') else 'false'}; then
        bbfatal "Not yet released. This recipe can only be used with MENDER_DEVMODE"
    fi
}
addtask do_version_check after do_unpack before do_install

do_install() {
    oe_runmake \
        -C ${S} \
        DESTDIR=${D} \
        install
}
