FILESEXTRAPATHS:prepend := "${THISDIR}/files:"

SRC_URI:append_vexpress-qemu = " file://restart-rngd.diff;patchdir=${WORKDIR}"
SRC_URI:append_vexpress-qemu-flash = " file://restart-rngd.diff;patchdir=${WORKDIR}"
