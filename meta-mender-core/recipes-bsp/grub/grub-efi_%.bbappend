inherit mender-helpers

FILESEXTRAPATHS_prepend := "${THISDIR}/files:"

SRC_URI_append = " \
    file://05_mender_setup_grub.cfg \
    file://90_mender_boot_grub.cfg \
    file://91_mender_try_to_recover_grub.cfg \
    file://blank_grubenv \
    file://mender_grubenv_check.inc \
    file://fw_printenv \
"

# Mender needs these.
GRUB_BUILDIN_append = " cat echo halt loadenv reboot"

PACKAGES_append = " ${PN}-mender-grubenv"
FILES_${PN}-mender-grubenv = " \
    ${sysconfdir}/grub/mender_grubenv_defines.inc \
    ${sysconfdir}/grub/mender_grubenv_check.inc \
    ${bindir}/fw_printenv \
    ${bindir}/fw_setenv \
"

do_provide_mender_defines() {
    :
}
do_provide_mender_defines_class-target() {
    set -x

    mender_rootfsa_part=$(get_part_number_from_device ${MENDER_ROOTFS_PART_A})
    mender_rootfsb_part=$(get_part_number_from_device ${MENDER_ROOTFS_PART_B})
    mender_grub_storage_device=$(get_grub_device_from_device_base ${MENDER_STORAGE_DEVICE_BASE})

    cat > ${WORKDIR}/mender_grubenv_defines.inc <<EOF
mender_rootfsa_part=$mender_rootfsa_part
mender_rootfsb_part=$mender_rootfsb_part
mender_kernel_root_base=${MENDER_STORAGE_DEVICE_BASE}
mender_grub_storage_device=$mender_grub_storage_device
EOF

    cp ${WORKDIR}/mender_grubenv_defines.inc ${WORKDIR}/00_mender_grubenv_defines_grub.cfg
    cp ${WORKDIR}/mender_grubenv_check.inc ${WORKDIR}/00_mender_grubenv_check_grub.cfg

    # Grub uses loads of '######' to fill the empty space, so find that
    # occurrence, and write our variables there.
    cp ${WORKDIR}/blank_grubenv ${WORKDIR}/mender_grubenv
    offset=$(grep '^######' -b ${WORKDIR}/mender_grubenv | egrep -o '^[0-9]+')
    dd of=${WORKDIR}/mender_grubenv bs=$offset seek=1 conv=notrunc <<EOF
bootcount=0
mender_boot_part=$(get_part_number_from_device ${MENDER_ROOTFS_PART_A})
upgrade_available=0
EOF
}
addtask do_provide_mender_defines after do_patch before do_compile

do_compile_append_class-target() {
    set -x

    # Inspired by the way grub-mkconfig and /etc/grub.d works. Note that unlike
    # the original, since we are not running on the target, these are dumped as
    # they are into a common script, not executed as grub-mkconfig does.
    for script in ${WORKDIR}/[0-9][0-9]_*_grub.cfg; do
        echo "# Start of ---------- $(basename $script) ----------"
        cat $script
        echo "# End of ---------- $(basename $script) ----------"
    done > ${WORKDIR}/mender_grub.cfg
}

do_install_append_class-target() {
    set -x

    mkdir -p ${D}/${sysconfdir}/grub
    install -m 644 ${WORKDIR}/mender_grubenv_defines.inc ${D}/${sysconfdir}/grub/
    install -m 644 ${WORKDIR}/mender_grubenv_check.inc ${D}/${sysconfdir}/grub/

    mkdir -p ${D}/${bindir}
    install -m 755 ${WORKDIR}/fw_printenv ${D}/${bindir}/fw_printenv
    ln -fs fw_printenv ${D}/${bindir}/fw_setenv
}

do_deploy_append_class-target() {
    set -x

    install -m 644 ${WORKDIR}/mender_grub.cfg ${DEPLOYDIR}/grub.cfg
    install -m 644 ${WORKDIR}/mender_grubenv ${DEPLOYDIR}/mender_grubenv1
    install -m 644 ${WORKDIR}/mender_grubenv ${DEPLOYDIR}/mender_grubenv2
}
