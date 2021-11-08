FILES:${PN}:append_mender-testing-enabled = " /data${nonarch_libdir}/os-release /data${sysconfdir}/os-release"
FILES:${PN}-staticdev:remove_mender-testing-enabled = "${nonarch_libdir}/os-release/*.a"
FILES:${PN}-dev:remove_mender-testing-enabled = "${nonarch_libdir}/os-release/*.la"
FILES:${PN}:remove_mender-testing-enabled = "${nonarch_libdir}/os-release/*"

do_install:append_mender-testing-enabled() {
    # Enable os-release to be changed from a R/O rootfs.

    mkdir -p ${D}/data${sysconfdir}
    cp ${D}${nonarch_libdir}/os-release ${D}/data${sysconfdir}/os-release
    rm -f ${D}${sysconfdir}/os-release
    ln -s /data${sysconfdir}/os-release ${D}${sysconfdir}/os-release

    mkdir -p ${D}/data${nonarch_libdir}
    mv ${D}${nonarch_libdir}/os-release ${D}/data${nonarch_libdir}/os-release
    ln -s /data${nonarch_libdir}/os-release ${D}${nonarch_libdir}/os-release
}