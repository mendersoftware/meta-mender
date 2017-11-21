do_install_append () {
    sed -i 's/^[#[:space:]]*PasswordAuthentication.*/PasswordAuthentication no/' ${D}${sysconfdir}/ssh/sshd_config
}
