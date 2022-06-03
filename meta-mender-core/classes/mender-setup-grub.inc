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
EFI_PROVIDER ?= ""
EFI_PROVIDER:mender-grub = "grub-efi"
EFI_PROVIDER:mender-grub:mender-bios = ""

# The bootloader which loads other EFI applications. On x86 this is generally
# provided by the firmware, and we specify empty. On ARM it is often provided by
# U-Boot, but it can also be provided EDK2, for example.
#
# Yocto doesn't have this concept, it only has EFI_PROVIDER (which, somewhat
# confusingly, does not name the provider of EFI, but the user of EFI). If Yocto
# had this we would probably call this variable EFI_LOADER, but let's stick with
# a MENDER prefix to avoid any future clashes.
MENDER_EFI_LOADER ??= "${_MENDER_EFI_LOADER_DEFAULT}"
_MENDER_EFI_LOADER_DEFAULT ?= ""
_MENDER_EFI_LOADER_DEFAULT:arm = "u-boot"
_MENDER_EFI_LOADER_DEFAULT:aarch64 = "u-boot"

python() {
    if d.getVar('MENDER_GRUB_STORAGE_DEVICE'):
        bb.fatal("MENDER_GRUB_STORAGE_DEVICE is deprecated. This is now dynamically determined at runtime.")
}

MENDER_FEATURES_ENABLE:append:mender-grub = " mender-efi-boot"
