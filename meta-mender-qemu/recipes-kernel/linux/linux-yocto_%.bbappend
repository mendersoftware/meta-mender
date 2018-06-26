FILESEXTRAPATHS_prepend := "${THISDIR}/${PN}:"

# Use custom defconfig in order to enable use of the vexpress model.
SRC_URI_append_vexpress-qemu = " file://defconfig \
                                file://vexpress-qemu-standard.scc \
                                file://reduce-memory-to-256m.patch \
                               " 
COMPATIBLE_MACHINE_vexpress-qemu = "vexpress-qemu"

# same config for vexpress-qemu-flash
SRC_URI_append_vexpress-qemu-flash = " file://defconfig \
                                       file://vexpress-qemu-standard.scc \
                                       file://reduce-memory-to-256m.patch \
                                       "

COMPATIBLE_MACHINE_vexpress-qemu-flash = "vexpress-qemu-flash"
