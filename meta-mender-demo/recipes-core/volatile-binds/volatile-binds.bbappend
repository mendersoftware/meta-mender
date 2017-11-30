do_install_append() {
    # Work around problem that /etc/resolv.conf is not created. Introduced by
    # commit fcd48092d7bca in poky.

    # If this test fails it's probably a sign that this workaround should be
    # removed.
    test -h ${D}${sysconfdir}/tmpfiles.d/etc.conf

    rm -f ${D}${sysconfdir}/tmpfiles.d/etc.conf
}
