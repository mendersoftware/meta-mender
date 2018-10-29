FILESEXTRAPATHS_prepend := "${THISDIR}/files:"
SRC_URI_append_arm = " file://02_qemu_console_arm_grub.cfg;subdir=git"
SRC_URI_append_x86-64 = " file://02_qemu_console_x86_grub.cfg;subdir=git"
