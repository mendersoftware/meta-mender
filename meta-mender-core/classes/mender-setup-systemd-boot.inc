# Mender systemd-boot support

EFI_PROVIDER:mender-systemd-boot = "systemd-boot"

# systemd-boot requires a slightly larger default boot partition
MENDER_BOOT_PART_SIZE_MB_DEFAULT:mender-systemd-boot = "64"

WKS_FILE_DEPENDS_BOOTLOADERS:remove:mender-systemd-boot = "grub-efi"

MENDER_FEATURES_ENABLE:append:mender-systemd-boot = " mender-efi-boot"
