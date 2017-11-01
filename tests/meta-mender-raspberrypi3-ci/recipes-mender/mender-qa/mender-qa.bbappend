PACKAGES += "gregs-rssh-tunnel"
FILESEXTRAPATHS_prepend := "${THISDIR}/files/rpi:"

SRC_URI_append = " file://rssh.service \
                   file://id_rsa \
                   file://id_rsa.pub"

FILES_${PN} += "${systemd_unitdir}/system/rssh.service \
                ${systemd_unitdir}/system/network.target.wants \
                ${datadir}/mender-qa/rssh \
                ${datadir}/mender-qa/rssh/id_rsa \
                ${datadir}/mender-qa/rssh/id_rsa.pub"


do_install_append() {
    install -d ${D}${systemd_unitdir}/system/network.target.wants  
    install -t ${D}${systemd_unitdir}/system ${WORKDIR}/rssh.service 
    ln -sf ../rssh.service ${D}${systemd_unitdir}/system/network.target.wants/

    install -d ${D}${datadir}/mender-qa/rssh
    install -t ${D}${datadir}/mender-qa/rssh/ ${WORKDIR}/id_rsa
    install -t ${D}${datadir}/mender-qa/rssh/ ${WORKDIR}/id_rsa.pub
}
