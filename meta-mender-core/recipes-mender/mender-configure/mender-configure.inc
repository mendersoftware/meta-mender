DESCRIPTION = "Mender add-on for device configuration."
HOMEPAGE = "https://mender.io"

RDEPENDS_${PN} = "dbus curl mender-client (>= 2.5)"

FILES_${PN} = " \
    ${datadir}/mender/modules/v3/mender-configure \
    ${datadir}/mender/inventory/mender-inventory-mender-configure \
    /var/lib/mender-configure \
    /data/mender-configure \
"

S = "${WORKDIR}/git"
B = "${WORKDIR}/build"

do_install() {
    oe_runmake \
        -C ${S} \
        DESTDIR=${D} \
        install

    install -d -m 755 ${D}/data/mender-configure
    install -d -m 755 ${D}/var/lib/
    ln -s /data/mender-configure ${D}/var/lib/mender-configure
}
