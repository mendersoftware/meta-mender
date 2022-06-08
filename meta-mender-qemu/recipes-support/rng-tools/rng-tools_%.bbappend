FILESEXTRAPATHS_prepend := "${THISDIR}/files:"

SRC_URI_append_vexpress-qemu = " file://restart-rngd.diff;patchdir=${WORKDIR}"
SRC_URI_append_vexpress-qemu-flash = " file://restart-rngd.diff;patchdir=${WORKDIR}"
