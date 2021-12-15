# Mender systemd-boot support

EFI_PROVIDER_mender-systemd-boot = "systemd-boot"

# systemd-boot requires a slightly larger default boot partition
MENDER_BOOT_PART_SIZE_MB_DEFAULT_mender-systemd-boot = "64"

WKS_FILE_DEPENDS_BOOTLOADERS_remove_mender-systemd-boot = "grub-efi"

MENDER_FEATURES_ENABLE_append_mender-systemd-boot = " mender-efi-boot"
