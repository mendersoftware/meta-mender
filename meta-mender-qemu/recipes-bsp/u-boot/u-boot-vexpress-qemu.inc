FILESEXTRAPATHS:prepend := "${THISDIR}/patches:${THISDIR}/files:"

SRC_URI:append_vexpress-qemu-flash = " file://0001-vexpress-qemu-specific-fixes-for-Flash.patch"
SRC_URI:append_vexpress-qemu-flash = " file://0001-Revert-cfi_flash-Fix-detection-of-8-bit-bus-flash-de.patch"
