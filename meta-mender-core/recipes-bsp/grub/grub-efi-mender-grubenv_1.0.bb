inherit mender-helpers
inherit deploy

LICENSE = "Apache-2.0"
LIC_FILES_CHKSUM = "file://LICENSE;md5=89aea4e17d99a7cacdbeed46a0096b10"
S = "${WORKDIR}"

FILESEXTRAPATHS_prepend := "${THISDIR}/files:"

# TODO: We should probably move some of these into a repository.
SRC_URI = " \
    file://LICENSE \
    file://05_mender_setup_grub.cfg \
    file://90_mender_boot_grub.cfg \
    file://91_mender_try_to_recover_grub.cfg \
    file://blank_grubenv \
    file://fw_printenv \
"

do_provide_mender_defines() {
    set -x

    mender_rootfsa_part=$(get_part_number_from_device ${MENDER_ROOTFS_PART_A})
    mender_rootfsb_part=$(get_part_number_from_device ${MENDER_ROOTFS_PART_B})
    mender_grub_storage_device=$(get_grub_device_from_device_base ${MENDER_STORAGE_DEVICE_BASE})

    cat > ${WORKDIR}/00_mender_grubenv_defines_grub.cfg <<EOF
mender_rootfsa_part=$mender_rootfsa_part
mender_rootfsb_part=$mender_rootfsb_part
mender_kernel_root_base=${MENDER_STORAGE_DEVICE_BASE}
mender_grub_storage_device=$mender_grub_storage_device
EOF

    # Environment files.

    # Grub uses loads of '######' to fill the empty space, so find that
    # occurrence, and write our variables there.
    mkdir -p ${WORKDIR}/mender_grubenv
    cp ${WORKDIR}/blank_grubenv ${WORKDIR}/mender_grubenv/env
    offset=$(grep '^######' -b ${WORKDIR}/mender_grubenv/env | egrep -o '^[0-9]+')
    dd of=${WORKDIR}/mender_grubenv/env bs=$offset seek=1 conv=notrunc <<EOF
bootcount=0
mender_boot_part=$(get_part_number_from_device ${MENDER_ROOTFS_PART_A})
upgrade_available=0
EOF

    # Lock files.

    cp ${WORKDIR}/blank_grubenv ${WORKDIR}/mender_grubenv/lock
    offset=$(grep '^######' -b ${WORKDIR}/mender_grubenv/lock | egrep -o '^[0-9]+')
    dd of=${WORKDIR}/mender_grubenv/lock bs=$offset seek=1 conv=notrunc <<EOF
editing=0
EOF
    ( cd ${WORKDIR}/mender_grubenv && sha256sum lock > lock.sha256sum )
}
addtask do_provide_mender_defines after do_patch before do_compile

do_compile() {
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

do_install() {
    set -x

    mkdir -p ${D}/${bindir}
    install -m 755 ${WORKDIR}/fw_printenv ${D}/${bindir}/fw_printenv
    ln -fs fw_printenv ${D}/${bindir}/fw_setenv
}

do_deploy() {
    set -x

    install -m 644 ${WORKDIR}/mender_grub.cfg ${DEPLOYDIR}/grub.cfg

    install -m 755 -d ${DEPLOYDIR}/mender_grubenv1
    install -m 644 ${WORKDIR}/mender_grubenv/env ${DEPLOYDIR}/mender_grubenv1/env
    install -m 644 ${WORKDIR}/mender_grubenv/lock ${DEPLOYDIR}/mender_grubenv1/lock
    install -m 644 ${WORKDIR}/mender_grubenv/lock.sha256sum ${DEPLOYDIR}/mender_grubenv1/lock.sha256sum
    install -m 755 -d ${DEPLOYDIR}/mender_grubenv2
    install -m 644 ${WORKDIR}/mender_grubenv/env ${DEPLOYDIR}/mender_grubenv2/env
    install -m 644 ${WORKDIR}/mender_grubenv/lock ${DEPLOYDIR}/mender_grubenv2/lock
    install -m 644 ${WORKDIR}/mender_grubenv/lock.sha256sum ${DEPLOYDIR}/mender_grubenv2/lock.sha256sum
}
addtask do_deploy after do_compile
