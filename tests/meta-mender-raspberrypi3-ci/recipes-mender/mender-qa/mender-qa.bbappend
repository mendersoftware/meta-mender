PACKAGES += "rssh-tunnel"
FILESEXTRAPATHS_prepend := "${THISDIR}/files/raspberrypi3:${THISDIR}/files/:"

SRC_URI_append = " file://rssh.service \
                   file://id_rsa \
                   file://id_rsa.pub \
                   file://authorized_keys"

FILES_${PN} += "${systemd_unitdir}/system/rssh.service \
                ${systemd_unitdir}/system/network.target.wants \
                ${datadir}/mender-qa/rssh \
                ${datadir}/mender-qa/rssh/id_rsa \
                ${datadir}/mender-qa/rssh/id_rsa.pub \
                /home/ \
                /home/root/ \
                /home/root/.ssh \
                /home/root/.ssh/authorized_keys"

do_install_append() {
    install -d ${D}${systemd_unitdir}/system/network.target.wants
    install -t ${D}${systemd_unitdir}/system ${WORKDIR}/rssh.service
    ln -sf ../rssh.service ${D}${systemd_unitdir}/system/network.target.wants/

    # install SSH keys
    install -d ${D}${datadir}/mender-qa/rssh
    install -m 400 -t ${D}${datadir}/mender-qa/rssh/ ${WORKDIR}/id_rsa
    install -m 400 -t ${D}${datadir}/mender-qa/rssh/ ${WORKDIR}/id_rsa.pub

    # install authorized keys
    install -d ${D}/home/root/.ssh/
    install -t ${D}/home/root/.ssh/ ${WORKDIR}/authorized_keys
}

