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

# See commit 28a1f5cd95cfd in poky. This was added in order to support running
# kernel tests. However it appears that this file is not present in the source
# at the time of writing. Rather than dig into this we will just remove this
# patch for now. This can probably be removed later when upstream has fixed this
# problem. (July 2018)
KERNEL_FEATURES_remove_qemuall = "features/kernel-sample/kernel-sample.scc"

# This doesn't appear in our config so remove it to avoid spurious warnings
KERNEL_FEATURES_remove_qemuall = "features/drm-bochs/drm-bochs.scc"
