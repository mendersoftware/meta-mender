# Pretty insecure to use the same SSH key on all devices, even for a demo image,
# but we need it for performance reasons on QEMU. So restrict it to QEMU.
RDEPENDS:${PN}-sshd:append:vexpress-qemu = " ssh-demo-keys"
RDEPENDS:${PN}-sshd:append:vexpress-qemu-flash = " ssh-demo-keys"
