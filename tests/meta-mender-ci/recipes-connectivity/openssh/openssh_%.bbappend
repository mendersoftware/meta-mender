do_install:append() {
    echo "" >> ${D}${sysconfdir}/ssh/sshd_config
    echo "# Removing limits on max connections so tests do not get limited" >> ${D}${sysconfdir}/ssh/sshd_config
    echo "LoginGraceTime 0" >> ${D}${sysconfdir}/ssh/sshd_config
    echo "MaxAuthTries 1000000" >> ${D}${sysconfdir}/ssh/sshd_config
    echo "MaxSessions 1000000" >> ${D}${sysconfdir}/ssh/sshd_config
    echo "MaxStartups 1000000" >> ${D}${sysconfdir}/ssh/sshd_config
}
