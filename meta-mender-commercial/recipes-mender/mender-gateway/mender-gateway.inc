inherit mender-licensing

inherit systemd

SUB_FOLDER_arm = "arm"
SUB_FOLDER_aarch64 = "aarch64"
SUB_FOLDER_x86-64 = "x86_64"

COMPATIBLE_HOSTS = "arm|aarch64|x86_64"

FILES_${PN} = " \
    ${bindir}/mender-gateway \
"

FILES_${PN}_append_mender-systemd = " \
    ${systemd_system_unitdir}/mender-gateway.service \
"

FILES_${PN}_append_mender-client-install = " \
    ${datadir}/mender/inventory/mender-inventory-mender-gateway \
"

S = "${WORKDIR}/mender-gateway-${PV}"

do_version_check() {
    if ! ${@'true' if d.getVar('MENDER_DEVMODE') else 'false'}; then
        if ! strings ${S}/${SUB_FOLDER}/mender-gateway | grep -q "^${PV}$"; then
            bbfatal "String '${PV}' not found in binary. Is it the correct version? Check with --version."
        fi
    fi
}
addtask do_version_check after do_unpack before do_install

SYSTEMD_SERVICE_${PN}_mender-systemd = "mender-gateway.service"

do_install() {
    install -d -m 755 ${D}${bindir}
    install -m 755 ${S}/${SUB_FOLDER}/mender-gateway ${D}${bindir}/mender-gateway
}

do_install_append_mender-systemd() {
    install -d -m 755 ${D}${systemd_unitdir}/system/
    install -m 644 ${S}/support/mender-gateway.service ${D}${systemd_unitdir}/system/mender-gateway.service
}

do_install_append_mender-client-install() {
    install -d -m 755 ${D}${datadir}/mender/inventory/
    install -m 775 ${S}/support/mender-inventory-mender-gateway ${D}${datadir}/mender/inventory/mender-inventory-mender-gateway
}
