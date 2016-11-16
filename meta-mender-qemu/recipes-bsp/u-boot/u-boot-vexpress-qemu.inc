FILESEXTRAPATHS_prepend_vexpress-qemu := "${THISDIR}/patches:"

SRC_URI_append_vexpress-qemu = " file://0001-Enable-U-Boot-on-QEMU-to-use-Mender-boot-code.patch \
                                 file://0003-Add-kernel-panic-option-to-vexpress-boot-arguments.patch"

BOOTENV_SIZE_vexpress-qemu ?= "0x40000"
