inherit mender-helpers
require conf/image-uefi.conf
inherit ${@bb.utils.contains('DISTRO_FEATURES', 'efi-secure-boot', 'user-key-store', '', d)}
inherit grub-mender-grubenv

RPROVIDES_${PN} += "virtual/grub-bootconf"

FILESEXTRAPATHS_prepend := "${THISDIR}/files:"

GRUB_CONF_LOCATION = "${EFI_FILES_PATH}"
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

SRC_URI_append = "${@bb.utils.contains('DISTRO_FEATURES', 'efi-secure-boot', ' file://01_efi_secure_boot_grub.cfg;subdir=git', '', d)}"

PACKAGECONFIG[debug-pause] = ",,,"
SRC_URI_append = "${@bb.utils.contains('PACKAGECONFIG', 'debug-pause', ' file://06_mender_debug_pause_grub.cfg;subdir=git', '', d)}"
PACKAGECONFIG[force-grub-prompt] = ",,,"
SRC_URI_append = "${@bb.utils.contains('PACKAGECONFIG', 'force-grub-prompt', ' file://06_mender_debug_force_grub_prompt_grub.cfg;subdir=git', '', d)}"
PACKAGECONFIG[debug-log] = ",,,"

RDEPENDS_${PN} = "grub-efi"
RDEPENDS_${PN}_mender-bios = "grub"
RPROVIDES_${PN} = "virtual/grub-bootconf"

# See https://www.gnu.org/software/grub/manual/grub/grub.html#debug
DEBUG_LOG_CATEGORY ?= "all"

do_provide_debug_log() {
    install -d ${B}
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

    cat > ${B}/mender_grubenv_defines <<EOF
mender_rootfsa_part=$mender_rootfsa_part
mender_rootfsb_part=$mender_rootfsb_part
mender_kernel_root_base=${MENDER_STORAGE_DEVICE_BASE}
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
}

do_compile() {
    set -x

    oe_runmake -f ${S}/Makefile srcdir=${S} ENV_DIR=${GRUB_CONF_LOCATION}
}

do_install() {
    set -x

    oe_runmake -f ${S}/Makefile srcdir=${S} ENV_DIR=${GRUB_CONF_LOCATION} DESTDIR=${D} install
}

python() {
    if bb.utils.contains('DISTRO_FEATURES', 'efi-secure-boot', True, False, d):
        bb.build.addtask('do_sign', 'do_deploy do_package', 'do_install', d)
        bb.build.addtask('do_chownboot', 'do_package', 'do_sign', d)
}

python do_sign() {
    uks_bl_sign("%s%s/grub.cfg" % (d.getVar("D"), d.getVar("GRUB_CONF_LOCATION")), d)
    uks_bl_sign("%s%s/mender_grubenv1/lock" % (d.getVar("D"), d.getVar("GRUB_CONF_LOCATION")), d)
    uks_bl_sign("%s%s/mender_grubenv2/lock" % (d.getVar("D"), d.getVar("GRUB_CONF_LOCATION")), d)
    uks_bl_sign("%s%s/mender_grubenv1/lock.sha256sum" % (d.getVar("D"), d.getVar("GRUB_CONF_LOCATION")), d)
    uks_bl_sign("%s%s/mender_grubenv2/lock.sha256sum" % (d.getVar("D"), d.getVar("GRUB_CONF_LOCATION")), d)
}
do_sign[prefuncs] += "${@bb.utils.contains('DISTRO_FEATURES', 'efi-secure-boot', 'check_deploy_keys', '', d)}"
do_sign[prefuncs] += "${@'check_boot_public_key' if d.getVar('GRUB_SIGN_VERIFY', True) == '1' else ''}"

fakeroot do_chownboot() {
    chown root:root -R "${D}${GRUB_CONF_LOCATION}/grub.cfg${SB_FILE_EXT}" \
           "${D}${GRUB_CONF_LOCATION}/mender_grubenv1/lock${SB_FILE_EXT}" \
           "${D}${GRUB_CONF_LOCATION}/mender_grubenv2/lock${SB_FILE_EXT}" \
           "${D}${GRUB_CONF_LOCATION}/mender_grubenv1/lock.sha256sum${SB_FILE_EXT}" \
           "${D}${GRUB_CONF_LOCATION}/mender_grubenv2/lock.sha256sum${SB_FILE_EXT}"
}
FILES_${PN}_append = "${@bb.utils.contains('DISTRO_FEATURES', 'efi-secure-boot', \
                                           ' \
                                             ${GRUB_CONF_LOCATION}/grub.cfg${SB_FILE_EXT} \
                                             ${GRUB_CONF_LOCATION}/mender_grubenv1/lock${SB_FILE_EXT} \
                                             ${GRUB_CONF_LOCATION}/mender_grubenv2/lock${SB_FILE_EXT} \
                                             ${GRUB_CONF_LOCATION}/mender_grubenv1/lock.sha256sum${SB_FILE_EXT} \
                                             ${GRUB_CONF_LOCATION}/mender_grubenv2/lock.sha256sum${SB_FILE_EXT} \
                                           ', '', d)}"
