# Mender systemd-boot support

EFI_PROVIDER_mender-systemd-boot = "systemd-boot"

# systemd-boot requires a slightly larger default boot partition
MENDER_BOOT_PART_SIZE_MB_DEFAULT_mender-systemd-boot = "64"

WKS_FILE_DEPENDS_BOOTLOADERS_remove_mender-systemd-boot = "grub-efi"

_MENDER_PART_IMAGE_DEPENDS_append_mender-systemd-boot = " \
    ${IMAGE_BASENAME}:do_uefiapp_deploy \
    "

MENDER_FEATURES_ENABLE += "mender-efi-boot"
