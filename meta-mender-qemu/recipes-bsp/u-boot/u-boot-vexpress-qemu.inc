FILESEXTRAPATHS:prepend := "${THISDIR}/patches:${THISDIR}/files:"

SRC_URI:append:vexpress-qemu-flash = " file://0001-vexpress-qemu-specific-fixes-for-Flash.patch"
SRC_URI:append:vexpress-qemu-flash = " file://0001-Revert-cfi_flash-Fix-detection-of-8-bit-bus-flash-de.patch"
SRC_URI:append:vexpress-qemu-flash = " file://no-flash-buffer-write.cfg"

# Drop vexpress's unpopulated 2nd DRAM bank, which otherwise hangs the uefi-grub
# boot at -m 256M. See the patch for details.
SRC_URI:append:vexpress-qemu = " file://0001-vexpress-drop-unpopulated-second-dram-bank.patch"
