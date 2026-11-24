FILESEXTRAPATHS:prepend := "${THISDIR}/patches:${THISDIR}/files:"

SRC_URI:append:vexpress-qemu-flash = " file://0001-vexpress-qemu-specific-fixes-for-Flash.patch"
SRC_URI:append:vexpress-qemu-flash = " file://0001-Revert-cfi_flash-Fix-detection-of-8-bit-bus-flash-de.patch"

# Drop vexpress's unpopulated 2nd DRAM bank, which otherwise hangs the uefi-grub
# boot at -m 256M. See the patch for details.
SRC_URI:append:vexpress-qemu = " file://0001-vexpress-drop-unpopulated-second-dram-bank.patch"

# The MMC/SD card is probed asynchronously, so on a slow boot the kernel can
# reach the rootfs mount before /dev/mmcblk0p3 is enumerated and panic with
# "VFS: Unable to mount root fs on unknown-block(0,0)". Append 'rootwait' to the
# kernel command line so the kernel waits for the root device instead of
# panicking. This fixes intermittent acceptance-test failures where the device
# never comes back after a reboot.
MENDER_UBOOT_PRE_SETUP_COMMANDS:vexpress-qemu:mender-uboot = "setenv bootargs \${bootargs} rootwait"
