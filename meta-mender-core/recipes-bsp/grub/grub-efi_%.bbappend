FILESEXTRAPATHS_prepend := "${THISDIR}/files:"
SRC_URI_append_cfg_file += " file://cfg"

include grub-mender.inc

EFI_BOOT_PATH ?= ""

FILES_${PN}_remove_mender-client-install = " /boot/EFI/BOOT/${GRUB_IMAGE} "
FILES_${PN}_append_mender-client-install = " ${MENDER_BOOT_PART_MOUNT_LOCATION}/EFI/BOOT/${GRUB_IMAGE} "

# When using mender and efi-secure-boot, these conf files will be provided by grub-mender-grubenv
CONFFILES_${PN}_remove_mender-grub = " \
    ${@bb.utils.contains('DISTRO_FEATURES', 'efi-secure-boot', '${EFI_BOOT_PATH}/grub.cfg', '', d)} \
    ${@bb.utils.contains('DISTRO_FEATURES', 'efi-secure-boot', '${EFI_BOOT_PATH}/grubenv', '', d)} \
    ${@bb.utils.contains('DISTRO_FEATURES', 'efi-secure-boot', '${EFI_BOOT_PATH}/boot-menu.inc', '', d)} \
    ${@bb.utils.contains('DISTRO_FEATURES', 'efi-secure-boot', '${EFI_BOOT_PATH}/efi-secure-boot.inc', '', d)} \
"

do_install_append_class-target() {
    if "${@bb.utils.contains('DISTRO_FEATURES', 'mender-client-install', 'true', 'false', d)}"; then
        install -d ${D}/${MENDER_BOOT_PART_MOUNT_LOCATION}
        mv ${D}/boot/EFI ${D}/${MENDER_BOOT_PART_MOUNT_LOCATION}
        rmdir ${D}/boot || true
    fi
}

# Allow the cfg and signature files to be installed by grub-mender-grubenv
python do_cleanconfigs_class-target() {
    if bb.utils.contains('DISTRO_FEATURES', 'mender-grub', True, False, d) and \
        bb.utils.contains('DISTRO_FEATURES', 'efi-secure-boot', True, False, d):
            ext = d.getVar("SB_FILE_EXT")
            for basename in ("grub.cfg", "grubenv", "boot-menu.inc", "efi-secure-boot.inc"):
                filebase = d.getVar("D") + d.getVar("MENDER_BOOT_PART_MOUNT_LOCATION") + "/EFI/BOOT/" + basename
                if os.path.exists(filebase):
                    os.remove(filebase)
                if os.path.exists(filebase + ext):
                    os.remove(filebase + ext)
}
python do_cleanconfigs() {
}
addtask cleanconfigs after do_sign do_chownboot before deploy do_package
