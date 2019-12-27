SRC_URI = " \
    file://dummy \
    file://dummy-with-different-content \
"
LICENSE = "PD"
LIC_FILES_CHKSUM = " \
    file://dummy;md5=b05403212c66bdc8ccc597fedf6cd5fe \
    file://dummy-with-different-content;md5=a23a5d316f134eed033e9185a5343543 \
"
S = "${WORKDIR}"

FILES_${PN} = "${MENDER_BOOT_PART_MOUNT_LOCATION}"

inherit deploy

do_install() {
    install -d -m 755 ${D}${MENDER_BOOT_PART_MOUNT_LOCATION}
    install -m 644 ${WORKDIR}/dummy ${D}${MENDER_BOOT_PART_MOUNT_LOCATION}/installed-test1
    install -d -m 755 ${D}${MENDER_BOOT_PART_MOUNT_LOCATION}/installed-test-dir2
    install -m 644 ${WORKDIR}/dummy ${D}${MENDER_BOOT_PART_MOUNT_LOCATION}/installed-test-dir2/installed-test2

    install -m 644 ${WORKDIR}/dummy ${D}${MENDER_BOOT_PART_MOUNT_LOCATION}/conflict-test1
    install -m 644 ${WORKDIR}/dummy ${D}${MENDER_BOOT_PART_MOUNT_LOCATION}/conflict-test2
}

do_deploy() {
    install -d -m 755 ${DEPLOYDIR}
    install -m 644 ${WORKDIR}/dummy ${DEPLOYDIR}/deployed-test1
    install -d -m 755 ${DEPLOYDIR}/deployed-test-dir2
    install -m 644 ${WORKDIR}/dummy ${DEPLOYDIR}/deployed-test-dir2/deployed-test2
    install -m 644 ${WORKDIR}/dummy ${DEPLOYDIR}/deployed-test3
    install -d -m 755 ${DEPLOYDIR}/deployed-test-dir4
    install -m 644 ${WORKDIR}/dummy ${DEPLOYDIR}/deployed-test-dir4/deployed-test4
    install -m 644 ${WORKDIR}/dummy ${DEPLOYDIR}/deployed-test5
    install -d -m 755 ${DEPLOYDIR}/deployed-test-dir6
    install -m 644 ${WORKDIR}/dummy ${DEPLOYDIR}/deployed-test-dir6/deployed-test6
    install -d -m 755 ${DEPLOYDIR}/deployed-test-dir7
    install -m 644 ${WORKDIR}/dummy ${DEPLOYDIR}/deployed-test-dir7/deployed-test7
    install -d -m 755 ${DEPLOYDIR}/deployed-test-dir8
    install -m 644 ${WORKDIR}/dummy ${DEPLOYDIR}/deployed-test-dir8/deployed-test8
    install -d -m 755 ${DEPLOYDIR}/deployed-test-dir9
    install -m 644 ${WORKDIR}/dummy ${DEPLOYDIR}/deployed-test-dir9/deployed-test9

    install -m 644 ${WORKDIR}/dummy ${DEPLOYDIR}/conflict-test1
    install -m 644 ${WORKDIR}/dummy-with-different-content ${DEPLOYDIR}/conflict-test2
}
addtask do_deploy after do_patch
