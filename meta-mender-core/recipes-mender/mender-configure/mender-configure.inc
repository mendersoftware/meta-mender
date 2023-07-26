inherit mender-licensing

DESCRIPTION = "Mender add-on for device configuration."
HOMEPAGE = "https://mender.io"

inherit systemd

PACKAGES:append = " ${PN}-demo ${PN}-scripts"

RDEPENDS:${PN} = "dbus curl mender-client (>= 2.5)"
RDEPENDS:${PN}-demo = "${PN} jq"
RDEPENDS:${PN}-scripts = "${PN} jq"

FILES:${PN} = " \
    ${datadir}/mender/modules/v3/mender-configure \
    ${datadir}/mender/inventory/mender-inventory-mender-configure \
    ${localstatedir}/lib/mender-configure \
    /data/mender-configure \
"

FILES:${PN}:append:mender-systemd = " \
    ${systemd_system_unitdir}/mender-configure-apply-device-config.service \
"

SYSTEMD_SERVICE:${PN}:mender-systemd = "mender-configure-apply-device-config.service"

# Note: Do not use ${libdir} below. It can be set to lib64, but the mender-configure sources are
# hardcoded to /usr/lib. Ideally this should be organized better, but changing it may have some side
# effects, so let's hardcode it for now.
FILES:${PN}-demo = " \
    /usr/lib/mender-configure/apply-device-config.d/mender-demo-raspberrypi-led \
    /data/mender-configure/device-config.json \
"

# Note: Do not use ${libdir} below. See above comment.
FILES:${PN}-scripts = " \
    /usr/lib/mender-configure/apply-device-config.d/timezone \
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
    install -d -m 755 ${D}/${localstatedir}/lib/
    ln -s /data/mender-configure ${D}/${localstatedir}/lib/mender-configure

    # For demo
    cat > ${D}/data/mender-configure/device-config.json <<EOF
{
  "timezone": "UTC"
EOF
    # Because of Bitbake parsing we have to jump through this hoop to get the
    # final '}' in.
    echo '}' >> ${D}/data/mender-configure/device-config.json
}

do_install:append:mender-systemd() {
    oe_runmake \
        -C ${S} \
        DESTDIR=${D} \
        install-systemd
}
