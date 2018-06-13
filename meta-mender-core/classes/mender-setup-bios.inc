# Make sure that GRUB is flashed to first non-partition table sector.
MENDER_IMAGE_BOOTLOADER_FILE_DEFAULT_mender-grub_mender-bios = "grub-core.img"
MENDER_IMAGE_BOOTLOADER_BOOTSECTOR_OFFSET_DEFAULT_mender-grub_mender-bios = "1"

# And that the 1st stage bootloader is in the MBR.
MENDER_MBR_BOOTLOADER_FILE_DEFAULT_mender-grub_mender-bios = "boot.img"

EXTRA_IMAGEDEPENDS_append_mender-grub_mender-bios = " grub"

_MENDER_GRUB_BOOT_FILES_mender-grub_mender-bios = " \
    grub.cfg;grub.cfg \
    mender_grubenv1/env;mender_grubenv1/env \
    mender_grubenv1/lock;mender_grubenv1/lock \
    mender_grubenv1/lock.sha256sum;mender_grubenv1/lock.sha256sum \
    mender_grubenv2/env;mender_grubenv2/env \
    mender_grubenv2/lock;mender_grubenv2/lock \
    mender_grubenv2/lock.sha256sum;mender_grubenv2/lock.sha256sum \
"
