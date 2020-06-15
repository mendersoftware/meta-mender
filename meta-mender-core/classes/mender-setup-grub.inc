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

python() {
    if d.getVar('MENDER_GRUB_STORAGE_DEVICE'):
        bb.fatal("MENDER_GRUB_STORAGE_DEVICE is deprecated. This is now dynamically determined at runtime.")
}
