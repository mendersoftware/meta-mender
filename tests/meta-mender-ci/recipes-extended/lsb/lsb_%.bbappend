FILES_${PN}_append = " /data${base_bindir}/lsb_release /data${bindir}/lsb_release"

do_install_append() {
    # Enable binary to be updated from R/O rootfs.

    mkdir -p ${D}/data${bindir}
    cp ${D}${base_bindir}/lsb_release ${D}/data${bindir}/lsb_release
    mkdir -p ${D}${bindir}
    ln -s /data${bindir}/lsb_release ${D}${bindir}/lsb_release

    mkdir -p ${D}/data${base_bindir}
    mv ${D}${base_bindir}/lsb_release ${D}/data${base_bindir}/lsb_release
    ln -s /data${base_bindir}/lsb_release ${D}${base_bindir}/lsb_release
}