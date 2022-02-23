FILESEXTRAPATHS:prepend := "${THISDIR}/patches:"

SRC_URI:append:arm_mender-grub = " file://0001-efi_loader-Omit-memory-with-no-map-when-returning-me.patch"
