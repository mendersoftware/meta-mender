FILESEXTRAPATHS_prepend := "${THISDIR}/files:"

SRC_URI_append = "\
               file://01-logs-to-console.conf \
               "
do_install_append() {
    install -d ${D}${sysconfdir}/systemd/journald.conf.d
    install -m 0644 -t ${D}${sysconfdir}/systemd/journald.conf.d \
            ${WORKDIR}/01-logs-to-console.conf
}

CONFFILES_${PN}_append = " ${sysconfdir}/systemd/journald.conf.d/01-logs-to-console.conf"
