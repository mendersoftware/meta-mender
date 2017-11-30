FILESEXTRAPATHS_prepend := "${THISDIR}/patches:${THISDIR}/files:"

SRC_URI_append_vexpress-qemu = " file://0001-Set-correct-load-addresses-for-QEMU.patch"

MENDER_UBOOT_AUTO_CONFIGURE_vexpress-qemu-flash = "0"
SRC_URI_append_vexpress-qemu-flash = " \
                                   file://0001-vexpress_ca9x4-enable-booting-from-ubifs.patch \
                                   file://0003-Add-kernel-panic-option-to-vexpress-boot-arguments.patch \
                                   file://0005-vexpress_ca9x4-Mender-with-UBIFS-integration.patch \
                                   file://fw_env.config.default \
                                   "

BOOTENV_SIZE_vexpress-qemu-flash ?= "0x40000"
