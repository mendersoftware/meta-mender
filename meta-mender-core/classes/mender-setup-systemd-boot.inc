# Mender systemd-boot support

EFI_PROVIDER_mender-systemd-boot = "systemd-boot"

# systemd-boot requires a slightly larger default boot partition
MENDER_BOOT_PART_SIZE_MB_DEFAULT_mender-systemd-boot = "64"

# Move required files into the image partition boot sector
EFI_ARCH_LOCAL ?= "x64"
EFI_BOOT_IMAGE ?= "boot${EFI_ARCH_LOCAL}.efi"
MENDER_IMAGE_BOOT_FILES_append_mender-systemd-boot = " \
	systemd-${EFI_BOOT_IMAGE};EFI/BOOT/${EFI_BOOT_IMAGE} \
	${IMAGE_LINK_NAME}.boot${EFI_ARCH_LOCAL}_a.efi;EFI/Linux/bootx64_a.efi \
	${IMAGE_LINK_NAME}.boot${EFI_ARCH_LOCAL}_b.efi;EFI/Linux/bootx64_b.efi \
	${IMAGE_LINK_NAME}.esp/loader/main/config*;loader/main/ \
	${IMAGE_LINK_NAME}.esp/loader/backup/config*;loader/backup/ \
	"

WKS_FILE_DEPENDS_BOOTLOADERS_remove_mender-systemd-boot = "grub-efi"

IMAGE_INSTALL_append = " systemd-mender-config"

PACKAGE_INSTALL_remove = " \
	initramfs-live-install \
	initramfs-module-install \
	"

_MENDER_PART_IMAGE_DEPENDS_append_mender-systemd-boot = " \
	${IMAGE_BASENAME}:do_uefiapp_deploy \
	"
