FILESEXTRAPATHS_prepend := "${THISDIR}/patches:${THISDIR}/files:"

# Remove this block when moving from dunfell to the next branch, and also remove
# the bundled version of u-boot_2021.07. See MEN-3915.
SRC_URI_append_mender-uboot = " \
    file://0001-gpio-Introduce-CONFIG_GPIO_EXTRA_HEADER-to-cleanup-i.patch \
    file://0001-ARM-vexpress_ca9x4-Reintroduce-board-in-order-to-use.patch \
"
SRC_URI_append_mender-grub_arm = " \
    file://0001-gpio-Introduce-CONFIG_GPIO_EXTRA_HEADER-to-cleanup-i.patch \
    file://0001-ARM-vexpress_ca9x4-Reintroduce-board-in-order-to-use.patch \
"

SRC_URI_append_vexpress-qemu = " file://0001-Set-correct-load-addresses-for-QEMU.patch"
SRC_URI_append_vexpress-qemu-flash = " file://0001-Set-correct-load-addresses-for-QEMU.patch"
SRC_URI_append_vexpress-qemu-flash = " file://0001-vexpress-qemu-specific-fixes-for-Flash.patch"
SRC_URI_append_vexpress-qemu-flash = " file://0001-Revert-cfi_flash-Fix-detection-of-8-bit-bus-flash-de.patch"
