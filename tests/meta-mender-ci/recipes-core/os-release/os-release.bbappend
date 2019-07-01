FILES_${PN}_append = " /data${nonarch_libdir}/os-release /data${sysconfdir}/os-release"
FILES_${PN}-staticdev_remove = "${nonarch_libdir}/os-release/*.a"
FILES_${PN}-dev_remove = "${nonarch_libdir}/os-release/*.la"
FILES_${PN}_remove = "${nonarch_libdir}/os-release/*"

do_install_append() {
    # Enable os-release to be changed from a R/O rootfs.

    mkdir -p ${D}/data${sysconfdir}
    cp ${D}${nonarch_libdir}/os-release ${D}/data${sysconfdir}/os-release
    rm -f ${D}${sysconfdir}/os-release
    ln -s /data${sysconfdir}/os-release ${D}${sysconfdir}/os-release

    mkdir -p ${D}/data${nonarch_libdir}
    mv ${D}${nonarch_libdir}/os-release ${D}/data${nonarch_libdir}/os-release
    ln -s /data${nonarch_libdir}/os-release ${D}${nonarch_libdir}/os-release
}