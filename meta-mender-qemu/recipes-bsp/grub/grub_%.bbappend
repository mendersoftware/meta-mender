FILESEXTRAPATHS_prepend := "${THISDIR}/files:"

SRC_URI_append = " file://01_mender_serial_console_grub.cfg"

# We need these because we use QEMU with -nographic argument.
GRUB_BUILDIN_append_mender-bios = " serial terminal"
