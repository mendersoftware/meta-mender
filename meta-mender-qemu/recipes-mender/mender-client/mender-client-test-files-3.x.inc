# Used as a rootfs-image replacement when testing update modules.
FILES:${PN}:append:mender-image:qemuall = " ${sysconfdir}/mender/rootfs-image-v2.conf \
                                            ${datadir}/mender/modules/v3/rootfs-image-v2"

do_compile:append:mender-image:qemuall() {
    if ${@bb.utils.contains('PACKAGECONFIG', 'modules', 'true', 'false', d)}; then
        cat > ${WORKDIR}/rootfs-image-v2.conf <<EOF
MENDER_ROOTFS_PART_A="${MENDER_ROOTFS_PART_A}"
MENDER_ROOTFS_PART_B="${MENDER_ROOTFS_PART_B}"
EOF
    fi
}

do_install:append:mender-image:qemuall() {
    if ${@bb.utils.contains('PACKAGECONFIG', 'modules', 'true', 'false', d)}; then
        install -m 755 -d ${D}${datadir}/mender/modules/v3
        install -m 755 ${B}/src/${GO_IMPORT}/tests/rootfs-image-v2 ${D}${datadir}/mender/modules/v3/

        install -m 755 -d ${D}${sysconfdir}/mender
        install -m 644 ${WORKDIR}/rootfs-image-v2.conf ${D}${sysconfdir}/mender/
    fi
}
