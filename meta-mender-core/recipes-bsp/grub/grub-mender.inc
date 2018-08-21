FILESEXTRAPATHS_prepend := "${THISDIR}/patches:"

# Mender needs these.
GRUB_BUILDIN_append_mender-grub = " cat echo gcry_sha256 halt hashsum loadenv sleep reboot"

GRUBPLATFORM_arm_mender-grub = "efi"

do_configure_prepend_mender-grub_class-target() {
    if [ "${KERNEL_IMAGETYPE}" = "uImage" ]; then
        bbfatal "GRUB is not compatible with KERNEL_IMAGETYPE = uImage. Please change it to either zImage or bzImage."
    fi
}
