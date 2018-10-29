# Make sure that GRUB is flashed to first non-partition table sector.
MENDER_IMAGE_BOOTLOADER_FILE_DEFAULT_mender-grub_mender-bios = "grub-core.img"
MENDER_IMAGE_BOOTLOADER_BOOTSECTOR_OFFSET_DEFAULT_mender-grub_mender-bios_mender-image-bios = "1"

# The first non-partition table sector of GPT is 34.
# https://en.wikipedia.org/wiki/GUID_Partition_Table
MENDER_IMAGE_BOOTLOADER_BOOTSECTOR_OFFSET_DEFAULT_mender-grub_mender-bios_mender-image-gpt = "34"

# And that the 1st stage bootloader is in the MBR.
MENDER_MBR_BOOTLOADER_FILE_DEFAULT_mender-grub_mender-bios = "boot.img"

EXTRA_IMAGEDEPENDS_append_mender-grub_mender-bios = " grub"
