inherit mender-helpers
inherit deploy

LICENSE = "Apache-2.0"
LIC_FILES_CHKSUM = "file://LICENSE;md5=89aea4e17d99a7cacdbeed46a0096b10"
S = "${WORKDIR}"

RPROVIDES_${PN} += "virtual/grub-bootconf"

FILESEXTRAPATHS_prepend := "${THISDIR}/files:"

FILES_${PN} += "/data/mender_grubenv.config"

# TODO: We should probably move some of these into a repository.
SRC_URI = " \
    file://LICENSE \
    file://05_mender_setup_grub.cfg \
    file://06_bootargs_grub.cfg \
    file://90_mender_boot_grub.cfg \
    file://95_mender_try_to_recover_grub.cfg \
    file://blank_grubenv \
    file://fw_printenv \
"

PACKAGECONFIG[debug-pause] = ",,,"
SRC_URI_append = "${@bb.utils.contains('PACKAGECONFIG', 'debug-pause', ' file://06_mender_debug_pause_grub.cfg', '', d)}"
PACKAGECONFIG[debug-log] = ",,,"

# See https://www.gnu.org/software/grub/manual/grub/grub.html#debug
DEBUG_LOG_CATEGORY ?= "all"

do_provide_debug_log() {
    install -d ${B}
    echo "debug=${DEBUG_LOG_CATEGORY}" > ${WORKDIR}/01_mender_debug_log_grub.cfg
}
python() {
    if bb.utils.contains('PACKAGECONFIG', 'debug-log', True, False, d):
        bb.build.addtask('do_provide_debug_log', 'do_patch', 'do_unpack', d)
}

do_provide_mender_defines() {
    set -x

    mender_rootfsa_part=$(get_part_number_from_device ${MENDER_ROOTFS_PART_A})
    mender_rootfsb_part=$(get_part_number_from_device ${MENDER_ROOTFS_PART_B})
    if [ -n "${MENDER_GRUB_STORAGE_DEVICE}" ]; then
        mender_grub_storage_device=${MENDER_GRUB_STORAGE_DEVICE}
    else
        mender_grub_storage_device=$(get_grub_device_from_device_base ${MENDER_STORAGE_DEVICE_BASE})
    fi

    cat > ${WORKDIR}/00_mender_grubenv_defines_grub.cfg <<EOF
mender_rootfsa_part=$mender_rootfsa_part
mender_rootfsb_part=$mender_rootfsb_part
mender_kernel_root_base=${MENDER_STORAGE_DEVICE_BASE}
mender_grub_storage_device=$mender_grub_storage_device
kernel_imagetype=${KERNEL_IMAGETYPE}
EOF

    if [ -n "${KERNEL_DEVICETREE}" ]; then
        MENDER_DTB_NAME=$(mender_get_clean_kernel_devicetree)
        cat >> ${WORKDIR}/00_mender_grubenv_defines_grub.cfg <<EOF
kernel_devicetree=$MENDER_DTB_NAME
EOF
    fi

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

    # Environment directory, which is root of boot partition for BIOS platforms,
    # and inside EFI/BOOT on UEFI platforms (the default).
    cat > ${B}/mender_grubenv.config <<EOF
ENV_DIR = ${MENDER_BOOT_PART_MOUNT_LOCATION}${@bb.utils.contains('DISTRO_FEATURES', 'mender-bios', '', '/EFI/BOOT', d)}
EOF
}

do_install() {
    set -x

    mkdir -p ${D}/${bindir}
    install -m 755 ${WORKDIR}/fw_printenv ${D}/${bindir}/fw_printenv
    ln -fs fw_printenv ${D}/${bindir}/fw_setenv

    mkdir -p ${D}/data
    install -m 444 ${B}/mender_grubenv.config ${D}/data/
    mkdir -p ${D}${sysconfdir}
    ln -fs /data/mender_grubenv.config ${D}${sysconfdir}/mender_grubenv.config
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
