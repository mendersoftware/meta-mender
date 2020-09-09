FILESEXTRAPATHS_prepend := "${THISDIR}/files:"
SRC_URI_append_cfg_file += " file://cfg"

include version_logic.inc

EFI_PROVIDER ?= "${_MENDER_EFI_PROVIDER_DEFAULT}"
_MENDER_EFI_PROVIDER_DEFAULT = ""
_MENDER_EFI_PROVIDER_DEFAULT_mender-grub = "grub-efi"
_MENDER_EFI_PROVIDER_DEFAULT_mender-grub_mender-bios = ""

do_check_config_efi_stub() {
}
do_check_config_efi_stub_mender-grub() {
    # The first "if" is just to make sure "file" is working correctly.
    if file -Lk ${DEPLOY_DIR_IMAGE}/${KERNEL_IMAGETYPE} | fgrep "Linux kernel"; then
        if ! file -Lk ${DEPLOY_DIR_IMAGE}/${KERNEL_IMAGETYPE} | fgrep "EFI application"; then
            bbwarn 'Kernel without CONFIG_EFI_STUB detected. This kernel will probably not boot with the current configuration (mender-grub). Mender tries to automatically apply the CONFIG_EFI_STUB configuration, but this does not always work. Consider adding the "enable_efi_stub.cfg" file, from the meta-mender repository, to the SRC_URI of your kernel recipe manually.'
        fi
    fi
}
do_check_config_efi_stub_mender-grub_mender-bios() {
}
addtask do_check_config_efi_stub before do_configure
do_check_config_efi_stub[depends] = "virtual/kernel:do_deploy"

include grub-mender.inc

EFI_BOOT_PATH ?= ""

# When using mender and efi-secure-boot, these conf files will be provided by grub-mender-grubenv
CONFFILES_${PN}_remove_mender-grub = " \
    ${@bb.utils.contains('DISTRO_FEATURES', 'efi-secure-boot', '${EFI_BOOT_PATH}/grub.cfg', '', d)} \
    ${@bb.utils.contains('DISTRO_FEATURES', 'efi-secure-boot', '${EFI_BOOT_PATH}/grubenv', '', d)} \
    ${@bb.utils.contains('DISTRO_FEATURES', 'efi-secure-boot', '${EFI_BOOT_PATH}/boot-menu.inc', '', d)} \
    ${@bb.utils.contains('DISTRO_FEATURES', 'efi-secure-boot', '${EFI_BOOT_PATH}/efi-secure-boot.inc', '', d)} \
"

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
