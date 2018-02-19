FILESEXTRAPATHS_prepend := "${THISDIR}/files:"

SRC_URI_append_vexpress-qemu-flash = " file://fw_env.config.default "

require u-boot-vexpress-qemu.inc
