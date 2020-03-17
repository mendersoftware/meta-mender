FILESEXTRAPATHS_prepend := "${THISDIR}/patches:"

# virtual/grub-bootconf will be removed by upstream recipes when using
# efi-secure-boot. However, we explicitly want to include grub-mender-grubenv.
RDEPENDS_${PN}_class-target_append_mender-client-install = " grub-mender-grubenv"

# Setup EFI_BOOT_PATH for meta-secure-core.
EFI_BOOT_PATH = "${MENDER_BOOT_PART_MOUNT_LOCATION}/EFI/BOOT"

# Mender needs these.
GRUB_BUILDIN_append_mender-grub = " cat echo gcry_sha256 halt hashsum loadenv sleep reboot test regexp"

GRUBPLATFORM_arm_mender-grub = "efi"

do_configure_prepend_mender-grub() {
    if [ "${KERNEL_IMAGETYPE}" = "uImage" ]; then
        bbfatal "GRUB is not compatible with KERNEL_IMAGETYPE = uImage. Please change it to either zImage or bzImage."
    fi
}
