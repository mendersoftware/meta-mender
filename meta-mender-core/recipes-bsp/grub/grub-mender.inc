FILESEXTRAPATHS:prepend:mender-grub := "${THISDIR}/patches:"

# virtual/grub-bootconf will be removed by upstream recipes when using
# efi-secure-boot. However, we explicitly want to include grub-mender-grubenv.
RDEPENDS:${PN}:class-target:append:mender-grub = " grub-mender-grubenv"

# Setup EFI_BOOT_PATH for meta-secure-core.
EFI_BOOT_PATH:mender-grub = "${MENDER_BOOT_PART_MOUNT_LOCATION}/EFI/BOOT"

# Mender needs these.
GRUB_BUILDIN:append:mender-grub = " cat echo gcry_sha256 halt hashsum loadenv sleep reboot test regexp"

GRUBPLATFORM:arm:mender-grub = "efi"

do_configure:prepend:mender-grub() {
    if [ "${KERNEL_IMAGETYPE}" = "uImage" ]; then
        bbfatal "GRUB is not compatible with KERNEL_IMAGETYPE = uImage. Please change it to either zImage or bzImage."
    fi
}
