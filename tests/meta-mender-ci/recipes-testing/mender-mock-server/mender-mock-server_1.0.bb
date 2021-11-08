SRC_URI = " \
    file://private.key \
    file://mender-mock-server.service \
    file://mender-mock-server.py \
"
LICENSE = "Apache-2.0"
LIC_FILES_CHKSUM = " \
    file://mender-mock-server.py;beginline=2;endline=14;md5=457f0d2d149c4d7f13339726a05c8b83 \
"
S = "${WORKDIR}"

RDEPENDS:${PN} = "python3-core python3-netserver"

inherit systemd

SYSTEMD_SERVICE:${PN} = "mender-mock-server.service"

FILES:${PN} += "\
    ${prefix}/local/bin/mender-mock-server.py \
    /data/mender-mock-server.py \
    ${prefix}/local/bin/private.key \
    ${systemd_unitdir}/system/mender-mock-server.service \
"

do_install() {
    install -d ${D}${prefix}/local/bin
    install -m 644 ${WORKDIR}/mender-mock-server.py ${D}${prefix}/local/bin/mender-mock-server.py
    install -m 600 ${WORKDIR}/private.key ${D}${prefix}/local/bin/private.key

    install -d ${D}/${systemd_unitdir}/system
    install -m 644 ${WORKDIR}/mender-mock-server.service ${D}${systemd_unitdir}/system/mender-mock-server.service

    install -m 755 -d ${D}/data
    mv ${D}${prefix}/local/bin/mender-mock-server.py ${D}/data/mender-mock-server.py
    ln -s /data/mender-mock-server.py ${D}${prefix}/local/bin/mender-mock-server.py
}
