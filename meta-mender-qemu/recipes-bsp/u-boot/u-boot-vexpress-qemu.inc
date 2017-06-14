FILESEXTRAPATHS_prepend := "${THISDIR}/patches:"

SRC_URI_append_vexpress-qemu = " file://0001-Enable-U-Boot-on-QEMU-to-use-Mender-boot-code.patch \
                                 file://0003-Add-kernel-panic-option-to-vexpress-boot-arguments.patch"

SRC_URI_append_vexpress-qemu-flash = " \
                                   file://0001-vexpress_ca9x4-enable-booting-from-ubifs.patch \
                                   file://0003-Add-kernel-panic-option-to-vexpress-boot-arguments.patch \
                                   file://0005-vexpress_ca9x4-Mender-with-UBIFS-integration.patch \
                                   "

BOOTENV_SIZE_vexpress-qemu ?= "0x40000"
BOOTENV_SIZE_vexpress-qemu-flash ?= "0x40000"
