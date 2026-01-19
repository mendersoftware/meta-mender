inherit mender-helpers
require conf/image-uefi.conf
inherit ${@bb.utils.contains('DISTRO_FEATURES', 'efi-secure-boot', 'user-key-store', '', d)}
inherit grub-mender-grubenv

FILESEXTRAPATHS:prepend := "${THISDIR}/files:"

# Location of grub.cfg in the filesystem hierarchy.
GRUB_CONF_LOCATION = "${EFI_FILES_PATH}"
GRUB_CONF_LOCATION:mender-bios = "${MENDER_BOOT_PART_MOUNT_LOCATION}"

# Location of grub.cfg within the boot partition.
GRUB_CONF_BARE_LOCATION = "${EFIDIR}"
GRUB_CONF_BARE_LOCATION:mender-bios = "/"

# Location of the boot partition. This is almost always equal to
# MENDER_BOOT_PART_MOUNT_LOCATION (which EFI_PREFIX is also equal to),
# but we allow it to be overridden here.
BOOT_DIR_LOCATION = "${EFI_PREFIX}"
BOOT_DIR_LOCATION:mender-bios = "${MENDER_BOOT_PART_MOUNT_LOCATION}"

# Location of the grub-mender-grubenv environment.
GRUB_ENV_LOCATION = "${MENDER_BOOT_PART_MOUNT_LOCATION}/grub-mender-grubenv"

FILES:${PN} += "/data/mender_grubenv.config \
                ${GRUB_CONF_LOCATION}/grub.cfg \
                ${GRUB_ENV_LOCATION}/mender_grubenv1/env \
                ${GRUB_ENV_LOCATION}/mender_grubenv1/lock \
                ${GRUB_ENV_LOCATION}/mender_grubenv1/lock.sha256sum \
                ${GRUB_ENV_LOCATION}/mender_grubenv2/env \
                ${GRUB_ENV_LOCATION}/mender_grubenv2/lock \
                ${GRUB_ENV_LOCATION}/mender_grubenv2/lock.sha256sum \
                ${sysconfdir}/mender_grubenv.config \
"

B = "${WORKDIR}/build"

SRC_URI:append = "${@bb.utils.contains('DISTRO_FEATURES', 'efi-secure-boot', ' file://01_efi_secure_boot_grub.cfg;subdir=git', '', d)}"

PACKAGECONFIG[debug-pause] = ",,,"
SRC_URI:append = "${@bb.utils.contains('PACKAGECONFIG', 'debug-pause', ' file://06_mender_debug_pause_grub.cfg;subdir=git', '', d)}"
PACKAGECONFIG[force-grub-prompt] = ",,,"
SRC_URI:append = "${@bb.utils.contains('PACKAGECONFIG', 'force-grub-prompt', ' file://06_mender_debug_force_grub_prompt_grub.cfg;subdir=git', '', d)}"
PACKAGECONFIG[debug-log] = ",,,"

RDEPENDS:${PN} = "grub-efi util-linux-flock"
RDEPENDS:${PN}:mender-bios = "grub util-linux-flock"

PROVIDES = "${@mender_feature_is_enabled('mender-grub', "virtual/grub-bootconf", "", d)}"
RPROVIDES:${PN} = "${@mender_feature_is_enabled('mender-grub', "virtual-grub-bootconf", "", d)}"

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

    if ${@bb.utils.contains('MENDER_FEATURES', 'mender-partuuid', 'true', 'false', d)}; then
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

    if ${@bb.utils.contains('MENDER_FEATURES', 'mender-partuuid', 'true', 'false', d)}; then
        mender_rootfsa_uuid=${@mender_get_partuuid_from_device(d, '${MENDER_ROOTFS_PART_A}')}
        mender_rootfsb_uuid=${@mender_get_partuuid_from_device(d, '${MENDER_ROOTFS_PART_B}')}
        cat >> ${B}/mender_grubenv_defines <<EOF
mender_rootfsa_uuid=$mender_rootfsa_uuid
mender_rootfsb_uuid=$mender_rootfsb_uuid
EOF
    fi

    oe_runmake -f ${S}/Makefile clean
}

do_compile() {
    set -x

    oe_runmake -f ${S}/Makefile srcdir=${S} BOOT_DIR=${BOOT_DIR_LOCATION} EFI_DIR=${GRUB_CONF_BARE_LOCATION}
}

do_install() {
    set -x

    oe_runmake -f ${S}/Makefile srcdir=${S} BOOT_DIR=${BOOT_DIR_LOCATION} EFI_DIR=${GRUB_CONF_BARE_LOCATION} DESTDIR=${D} install-standalone
}

do_install:append:mender-bios() {
    # For BIOS installations, the boot partition is normally found in a
    # nonstandard location like `/boot/grub`, so record that.
    install -m 755 -d ${D}${sysconfdir}
    echo "ENV_DIR = ${GRUB_ENV_LOCATION}" > ${D}${sysconfdir}/mender_grubenv.config
}

python() {
    if bb.utils.contains('DISTRO_FEATURES', 'efi-secure-boot', True, False, d):
        bb.build.addtask('do_sign', 'do_deploy do_package', 'do_install', d)
        bb.build.addtask('do_chownboot', 'do_deploy do_package', 'do_sign', d)
}

python do_sign() {
    uks_bl_sign("%s%s/grub.cfg" % (d.getVar("D"), d.getVar("GRUB_CONF_LOCATION")), d)
    uks_bl_sign("%s%s/mender_grubenv1/lock" % (d.getVar("D"), d.getVar("GRUB_ENV_LOCATION")), d)
    uks_bl_sign("%s%s/mender_grubenv2/lock" % (d.getVar("D"), d.getVar("GRUB_ENV_LOCATION")), d)
    uks_bl_sign("%s%s/mender_grubenv1/lock.sha256sum" % (d.getVar("D"), d.getVar("GRUB_ENV_LOCATION")), d)
    uks_bl_sign("%s%s/mender_grubenv2/lock.sha256sum" % (d.getVar("D"), d.getVar("GRUB_ENV_LOCATION")), d)
}
do_sign[prefuncs] += "${@bb.utils.contains('DISTRO_FEATURES', 'efi-secure-boot', 'check_deploy_keys', '', d)}"
do_sign[prefuncs] += "${@'check_boot_public_key' if d.getVar('GRUB_SIGN_VERIFY', True) == '1' else ''}"

fakeroot do_chownboot() {
    chown root:root -R "${D}${GRUB_CONF_LOCATION}/grub.cfg${SB_FILE_EXT}" \
           "${D}${GRUB_ENV_LOCATION}/mender_grubenv1/lock${SB_FILE_EXT}" \
           "${D}${GRUB_ENV_LOCATION}/mender_grubenv2/lock${SB_FILE_EXT}" \
           "${D}${GRUB_ENV_LOCATION}/mender_grubenv1/lock.sha256sum${SB_FILE_EXT}" \
           "${D}${GRUB_ENV_LOCATION}/mender_grubenv2/lock.sha256sum${SB_FILE_EXT}"
}
FILES:${PN}:append = "${@bb.utils.contains('DISTRO_FEATURES', 'efi-secure-boot', \
                                           ' \
                                             ${GRUB_CONF_LOCATION}/grub.cfg${SB_FILE_EXT} \
                                             ${GRUB_ENV_LOCATION}/mender_grubenv1/lock${SB_FILE_EXT} \
                                             ${GRUB_ENV_LOCATION}/mender_grubenv2/lock${SB_FILE_EXT} \
                                             ${GRUB_ENV_LOCATION}/mender_grubenv1/lock.sha256sum${SB_FILE_EXT} \
                                             ${GRUB_ENV_LOCATION}/mender_grubenv2/lock.sha256sum${SB_FILE_EXT} \
                                           ', '', d)}"
