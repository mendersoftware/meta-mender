FILESEXTRAPATHS:prepend_mender-grub := "${THISDIR}/files:"

SRC_URI:append_mender-grub = " file://01_mender_serial_console_grub.cfg"

# We need these because we use QEMU with -nographic argument.
GRUB_BUILDIN:append_mender-bios = " serial terminal"
