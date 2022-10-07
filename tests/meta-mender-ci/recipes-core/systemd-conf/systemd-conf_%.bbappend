FILESEXTRAPATHS:prepend:mender-systemd := "${THISDIR}/files:"

SRC_URI:append:mender-systemd = " \
    file://journald.conf \
"

FILES:${PN}:append:mender-systemd = " \
    ${sysconfdir}/systemd/journald.conf.d/00-journal-size.conf \
"

do_install:append:mender-systemd() {
        install -d ${D}${sysconfdir}/systemd/journald.conf.d/
        install -m 0644 ${WORKDIR}/journald.conf ${D}${sysconfdir}/systemd/journald.conf.d/00-journal-size.conf
}
