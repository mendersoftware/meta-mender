PACKAGES:append:mender-testing-enabled = " rssh-tunnel"
FILESEXTRAPATHS:prepend:mender-testing-enabled := "${THISDIR}/files/beagleboneblack/:${THISDIR}/files/:"

SRC_URI:append:mender-testing-enabled = " \
                   file://rssh.service \
                   file://id_rsa \
                   file://id_rsa.pub \
                   file://authorized_keys \
                   file://uEnv.txt"

FILES:${PN}:append:mender-testing-enabled = " \
                ${systemd_unitdir}/system/rssh.service \
                ${systemd_unitdir}/system/network.target.wants \
                ${datadir}/mender-qa/rssh \
                ${datadir}/mender-qa/rssh/id_rsa \
                ${datadir}/mender-qa/rssh/id_rsa.pub \
                /home/ \
                /home/root/ \
                /home/root/.ssh \
                /home/root/.ssh/authorized_keys"

do_install:append:mender-testing-enabled() {
    install -m 0644 -t ${D}${datadir}/mender-qa ${WORKDIR}/uEnv.txt

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
