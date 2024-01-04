FILESEXTRAPATHS:prepend:mender-update-install := "${THISDIR}/files:"
SRC_URI:append:arm:mender-update-install = " file://02_qemu_console_arm_grub.cfg;subdir=git"
SRC_URI:append:x86-64:mender-update-install = " file://02_qemu_console_x86_grub.cfg;subdir=git"
