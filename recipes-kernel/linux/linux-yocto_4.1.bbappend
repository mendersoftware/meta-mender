# Use custom defconfig in order to enable use of the vexpress model.
FILESEXTRAPATHS_prepend := "${THISDIR}/${PN}:"
SRC_URI_append_vexpress-qemu += "file://defconfig"

KBRANCH_vexpress-qemu ?= "master"
SRCREV_machine_vexpress-qemu ?= "86093f78f63392d70228887796a591e7c1f0804e"
SRCREV_meta_vexpress-qemu = "46bb64d605fd336d99fa05bab566b9553b40b4b4"

COMPATIBLE_MACHINE_append = "|vexpress-qemu"
