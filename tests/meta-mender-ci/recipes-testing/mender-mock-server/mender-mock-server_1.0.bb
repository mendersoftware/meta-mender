SRC_URI = " \
    file://private.key \
    file://mender-mock-server.service \
    file://mender-mock-server.py \
"
LICENSE = "PD"
LIC_FILES_CHKSUM = " \
    file://private.key;md5=8a1986b43cf91bb9f47b0af99ad764fd \
    file://mender-mock-server.service;md5=38751b3b7fe2ab6dbcacaad792128b9a \
    file://mender-mock-server.py;md5=958275eda2dd2fe87d6ce649fc5599c3 \
"
S = "${WORKDIR}"

inherit systemd

SYSTEMD_SERVICE_${PN} = "mender-mock-server.service"

FILES_${PN} += "\
    ${prefix}/local/bin/mender-mock-server.py \
    ${prefix}/local/bin/private.key \
    ${systemd_unitdir}/system/mender-mock-server.service \
"

do_install() {
    install -d ${D}${prefix}/local/bin
    install -m 644 ${WORKDIR}/mender-mock-server.py ${D}${prefix}/local/bin/mender-mock-server.py
    install -m 600 ${WORKDIR}/private.key ${D}${prefix}/local/bin/private.key

    install -d ${D}/${systemd_unitdir}/system
    install -m 644 ${WORKDIR}/mender-mock-server.service ${D}${systemd_unitdir}/system/mender-mock-server.service
}
