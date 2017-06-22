# Use custom defconfig in order to enable use of the vexpress model.
FILESEXTRAPATHS_prepend := "${THISDIR}/${PN}:"
SRC_URI_append_vexpress-qemu = " file://defconfig \
                                file://vexpress-qemu-standard.scc \
                               " 
COMPATIBLE_MACHINE_vexpress-qemu = "vexpress-qemu"

# same config for vexpress-qemu-flash
SRC_URI_append_vexpress-qemu-flash = " file://defconfig \
                                       file://vexpress-qemu-standard.scc \
                                       "

COMPATIBLE_MACHINE_vexpress-qemu-flash = "vexpress-qemu-flash"
