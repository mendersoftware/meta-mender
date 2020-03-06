EXTRA_IMAGEDEPENDS_append_mender-grub = " grub-efi"

# The device number of the interface to load partitions from. This is normally
# empty, in which case it is deduced from MENDER_STORAGE_DEVICE. Only use this
# if the indexing of devices is different in Grub and in the Linux kernel.
MENDER_GRUB_STORAGE_DEVICE ??= "${MENDER_GRUB_STORAGE_DEVICE_DEFAULT}"
MENDER_GRUB_STORAGE_DEVICE_DEFAULT = ""

IMAGE_BOOT_FILES_append_mender-grub = "${_MENDER_GRUB_BOOT_FILES}"

_MENDER_GRUB_BOOT_FILES = ""
_MENDER_GRUB_BOOT_FILES_mender-grub = " \
    grub.cfg;EFI/BOOT/grub.cfg \
    mender_grubenv1/env;EFI/BOOT/mender_grubenv1/env \
    mender_grubenv1/lock;EFI/BOOT/mender_grubenv1/lock \
    mender_grubenv1/lock.sha256sum;EFI/BOOT/mender_grubenv1/lock.sha256sum \
    mender_grubenv2/env;EFI/BOOT/mender_grubenv2/env \
    mender_grubenv2/lock;EFI/BOOT/mender_grubenv2/lock \
    mender_grubenv2/lock.sha256sum;EFI/BOOT/mender_grubenv2/lock.sha256sum \
"
_MENDER_GRUB_BOOT_FILES_append_mender-grub_arm = " grub-efi-bootarm.efi;EFI/BOOT/bootarm.efi"
_MENDER_GRUB_BOOT_FILES_append_mender-grub_x86 = " grub-efi-bootia32.efi;EFI/BOOT/bootia32.efi"
_MENDER_GRUB_BOOT_FILES_append_mender-grub_x86-64 = " grub-efi-bootx64.efi;EFI/BOOT/bootx64.efi"

# We want to use upstream grub variants if possible. However, we have recipes
# that will be enabled in some configurations where COMPATIBLE_HOSTS doesn't
# match for the upstream recipe. See the recipes-bsp/grub folder.
PREFERRED_PROVIDER_grub-efi ?= "grub-efi"
PREFERRED_RPROVIDER_grub-efi ?= "grub-efi"
PREFERRED_PROVIDER_grub-editenv ?= "grub"
PREFERRED_RPROVIDER_grub-editenv ?= "grub"

PREFERRED_PROVIDER_virtual/grub-bootconf ?= "grub-mender-grubenv"
PREFERRED_RPROVIDER_virtual/grub-bootconf ?= "grub-mender-grubenv"

# Set EFI_PROVIDER.  Not all MACHINE configs use it but notably
# intel-corei7-64 does and without this we use the default of systemd-boot.
EFI_PROVIDER_mender-grub="grub-efi"
