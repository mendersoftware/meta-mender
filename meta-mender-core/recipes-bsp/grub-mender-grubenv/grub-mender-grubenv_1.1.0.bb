inherit mender-helpers

SRC_URI = "git://github.com/mendersoftware/grub-mender-grubenv;protocol=https;branch=master"

# Tag: 1.1.0
SRCREV = "197adb59cd65c966d7da61baf859a14aaa2949ad"

LICENSE = "Apache-2.0"
LIC_FILES_CHKSUM = "file://LICENSE;md5=a63d325b69180ec25a59e045c06ec468"

FILESEXTRAPATHS_prepend := "${THISDIR}/files:"

GRUB_CONF_LOCATION = "${MENDER_BOOT_PART_MOUNT_LOCATION}/EFI/BOOT"
GRUB_CONF_LOCATION_mender-bios = "${MENDER_BOOT_PART_MOUNT_LOCATION}"

FILES_${PN} += "/data/mender_grubenv.config \
                ${GRUB_CONF_LOCATION}/grub.cfg \
                ${GRUB_CONF_LOCATION}/mender_grubenv1/env \
                ${GRUB_CONF_LOCATION}/mender_grubenv1/lock \
                ${GRUB_CONF_LOCATION}/mender_grubenv1/lock.sha256sum \
                ${GRUB_CONF_LOCATION}/mender_grubenv2/env \
                ${GRUB_CONF_LOCATION}/mender_grubenv2/lock \
                ${GRUB_CONF_LOCATION}/mender_grubenv2/lock.sha256sum \
"

S = "${WORKDIR}/git"
B = "${WORKDIR}/build"

PACKAGECONFIG[debug-pause] = ",,,"
SRC_URI_append = "${@bb.utils.contains('PACKAGECONFIG', 'debug-pause', ' file://06_mender_debug_pause_grub.cfg', '', d)}"
PACKAGECONFIG[debug-log] = ",,,"

# See https://www.gnu.org/software/grub/manual/grub/grub.html#debug
DEBUG_LOG_CATEGORY ?= "all"

do_provide_debug_log() {
    echo "debug=${DEBUG_LOG_CATEGORY}" > ${B}/01_mender_debug_log_grub.cfg
}
python() {
    if bb.utils.contains('PACKAGECONFIG', 'debug-log', True, False, d):
        bb.build.addtask('do_provide_debug_log', 'do_patch', 'do_unpack', d)
}

do_configure() {
    set -x

    if ${@bb.utils.contains('DISTRO_FEATURES', 'mender-partuuid', 'true', 'false', d)}; then
        mender_rootfsa_part=${MENDER_ROOTFS_PART_A_NUMBER}
        mender_rootfsb_part=${MENDER_ROOTFS_PART_B_NUMBER}
    else
        mender_rootfsa_part=$(get_part_number_from_device ${MENDER_ROOTFS_PART_A})
        mender_rootfsb_part=$(get_part_number_from_device ${MENDER_ROOTFS_PART_B})
    fi

    if [ -n "${MENDER_GRUB_STORAGE_DEVICE}" ]; then
        mender_grub_storage_device=${MENDER_GRUB_STORAGE_DEVICE}
    elif ${@bb.utils.contains('DISTRO_FEATURES', 'mender-partuuid', 'true', 'false', d)}; then
        bbfatal "MENDER_GRUB_STORAGE_DEVICE is required for mender-partuuid"
    else
        mender_grub_storage_device=$(get_grub_device_from_device_base ${MENDER_STORAGE_DEVICE_BASE})
    fi

    cat > ${B}/mender_grubenv_defines <<EOF
mender_rootfsa_part=$mender_rootfsa_part
mender_rootfsb_part=$mender_rootfsb_part
mender_kernel_root_base=${MENDER_STORAGE_DEVICE_BASE}
mender_grub_storage_device=$mender_grub_storage_device
kernel_imagetype=${KERNEL_IMAGETYPE}
EOF

    if ${@bb.utils.contains('DISTRO_FEATURES', 'mender-partuuid', 'true', 'false', d)}; then
        mender_rootfsa_uuid=${@mender_get_partuuid_from_device(d, '${MENDER_ROOTFS_PART_A}')}
        mender_rootfsb_uuid=${@mender_get_partuuid_from_device(d, '${MENDER_ROOTFS_PART_B}')}
        cat >> ${B}/mender_grubenv_defines <<EOF
mender_rootfsa_uuid=$mender_rootfsa_uuid
mender_rootfsb_uuid=$mender_rootfsb_uuid
EOF
    fi

    if [ -n "${KERNEL_DEVICETREE}" ]; then
        MENDER_DTB_NAME=$(mender_get_clean_kernel_devicetree)
        cat >> ${B}/mender_grubenv_defines <<EOF
kernel_devicetree=$MENDER_DTB_NAME
EOF
    fi
}

do_compile() {
    set -x

    oe_runmake -f ${S}/Makefile srcdir=${S} ENV_DIR=${GRUB_CONF_LOCATION}
}

do_install() {
    set -x

    oe_runmake -f ${S}/Makefile srcdir=${S} ENV_DIR=${GRUB_CONF_LOCATION} DESTDIR=${D} install
}
