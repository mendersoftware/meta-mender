inherit mender-licensing

DESCRIPTION = "Mender Container Modules"
HOMEPAGE = "https://mender.io"

PACKAGES =+ "mender-docker-compose"

RDEPENDS:mender-docker-compose = "mender-update docker-compose docker jq"

FILES:mender-docker-compose = " \
    ${datadir}/mender/modules/v3/docker-compose \
"

FILES:mender-docker-compose:append:mender-image = " \
    /var/lib/mender-docker-compose \
    /data/mender-docker-compose \
    /etc/mender/mender-docker-compose.conf \
"

S = "${WORKDIR}/git"
B = "${WORKDIR}/build"

do_configure:mender-image() {
    echo 'PERSISTENT_STORE="/var/lib/mender-docker-compose"' > ${WORKDIR}/mender-docker-compose.conf
}

do_install() {
    oe_runmake \
        -C ${S} \
        DESTDIR=${D} \
        prefix=${D} \
        install
}

do_install:append:mender-image() {
    # symlink
    install -m 755 -d ${D}/data/mender-docker-compose
    install -d -m 755 ${D}/${localstatedir}/lib/
    ln -s /data/mender-docker-compose ${D}/${localstatedir}/lib/mender-docker-compose

    # config file
    install -d -m 755 ${D}${sysconfdir}/mender/
    install -m 644 ${WORKDIR}/mender-docker-compose.conf ${D}${sysconfdir}/mender/mender-docker-compose.conf
}
