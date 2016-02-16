# Keep this separately from the rest of the .bb file in case that .bb file is
# overridden from another layer.

FILESEXTRAPATHS_prepend := "${THISDIR}/files:"
SRC_URI += "file://0001-Enable-boot-code-specifically-for-the-U-Boot-QEMU-sc.patch"
