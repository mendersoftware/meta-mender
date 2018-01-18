# Pretty insecure to use the same SSH key on all devices, even for a demo image,
# but we need it for performance reasons on QEMU. So restrict it to QEMU.
RDEPENDS_${PN}-sshd_append_vexpress-qemu = " ssh-demo-keys"
RDEPENDS_${PN}-sshd_append_vexpress-qemu-flash = " ssh-demo-keys"
