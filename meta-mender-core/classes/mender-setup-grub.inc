EXTRA_IMAGEDEPENDS_append = "${@bb.utils.contains('DISTRO_FEATURES', 'mender-grub', ' grub-efi', '', d)}"

# The device number of the interface to load partitions from. This is normally
# empty, in which case it is deduced from MENDER_STORAGE_DEVICE. Only use this
# if the indexing of devices is different in Grub and in the Linux kernel.
MENDER_GRUB_STORAGE_DEVICE ??= "${MENDER_GRUB_STORAGE_DEVICE_DEFAULT}"
MENDER_GRUB_STORAGE_DEVICE_DEFAULT = ""

IMAGE_BOOT_FILES_append_mender-grub = " \
    grub-efi-bootx64.efi;EFI/BOOT/bootx64.efi \
    grub.cfg;EFI/BOOT/grub.cfg \
    mender_grubenv1/env;EFI/BOOT/mender_grubenv1/env \
    mender_grubenv1/lock;EFI/BOOT/mender_grubenv1/lock \
    mender_grubenv1/lock.sha256sum;EFI/BOOT/mender_grubenv1/lock.sha256sum \
    mender_grubenv2/env;EFI/BOOT/mender_grubenv2/env \
    mender_grubenv2/lock;EFI/BOOT/mender_grubenv2/lock \
    mender_grubenv2/lock.sha256sum;EFI/BOOT/mender_grubenv2/lock.sha256sum \
"
