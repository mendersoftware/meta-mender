# A recipe which installs dummy symlinks for lsb_release. This tool is not
# supported anymore on Yocto/zeus and later, but we retain it for testing the
# logic in the Mender client, in case it is used on a system which does have
# support.

LICENSE = "Apache-2.0"

FILES_${PN} = " \
    ${base_bindir}/lsb_release \
    ${bindir}/lsb_release \
    /data${base_bindir} \
    /data${bindir} \
"

do_install() {
    # Enable binary to be updated from R/O rootfs.

    mkdir -p ${D}/data${bindir}
    mkdir -p ${D}${bindir}
    ln -s /data${bindir}/lsb_release ${D}${bindir}/lsb_release

    mkdir -p ${D}/data${base_bindir}
    mkdir -p ${D}${base_bindir}
    ln -s /data${base_bindir}/lsb_release ${D}${base_bindir}/lsb_release
}
