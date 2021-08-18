FILESEXTRAPATHS_prepend := "${THISDIR}/patches:${THISDIR}/files:"

SRC_URI_append_vexpress-qemu = " file://0001-Set-correct-load-addresses-for-QEMU.patch"
SRC_URI_append_vexpress-qemu-flash = " file://0001-Set-correct-load-addresses-for-QEMU.patch"
SRC_URI_append_vexpress-qemu-flash = " file://0001-vexpress-qemu-specific-fixes-for-Flash.patch"
SRC_URI_append_vexpress-qemu-flash = " file://0001-Revert-cfi_flash-Fix-detection-of-8-bit-bus-flash-de.patch"
