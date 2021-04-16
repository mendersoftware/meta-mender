DESCRIPTION = "Mender add-on for device configuration."
HOMEPAGE = "https://mender.io"

inherit systemd

PACKAGES_append = " ${PN}-demo ${PN}-scripts"

RDEPENDS_${PN} = "dbus curl mender-client (>= 2.5)"
RDEPENDS_${PN}-demo = "${PN} jq"
RDEPENDS_${PN}-scripts = "${PN} jq"

FILES_${PN} = " \
    ${datadir}/mender/modules/v3/mender-configure \
    ${datadir}/mender/inventory/mender-inventory-mender-configure \
    /var/lib/mender-configure \
    /data/mender-configure \
"

FILES_${PN}_append_mender-systemd = " \
    ${systemd_system_unitdir}/mender-configure-apply-device-config.service \
"

SYSTEMD_SERVICE_${PN} = "mender-configure-apply-device-config.service"

FILES_${PN}-demo = " \
    ${libdir}/mender-configure/apply-device-config.d/mender-demo-raspberrypi-led \
    /data/mender-configure/device-config.json \
"

FILES_${PN}-scripts = " \
    ${libdir}/mender-configure/apply-device-config.d/timezone \
"

S = "${WORKDIR}/git"
B = "${WORKDIR}/build"

do_install() {
    oe_runmake \
        -C ${S} \
        DESTDIR=${D} \
        install-bin \
        install-demo \
        install-scripts

    install -d -m 755 ${D}/data/mender-configure
    install -d -m 755 ${D}/var/lib/
    ln -s /data/mender-configure ${D}/var/lib/mender-configure

    # For demo
    cat > ${D}/data/mender-configure/device-config.json <<EOF
{
  "timezone": "UTC"
EOF
    # Because of Bitbake parsing we have to jump through this hoop to get the
    # final '}' in.
    echo '}' >> ${D}/data/mender-configure/device-config.json
}

do_install_append_mender-systemd() {
    oe_runmake \
        -C ${S} \
        DESTDIR=${D} \
        install-systemd
}
