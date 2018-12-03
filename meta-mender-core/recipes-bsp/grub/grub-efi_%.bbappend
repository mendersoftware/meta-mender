FILESEXTRAPATHS_prepend := "${THISDIR}/files:"
SRC_URI_append_cfg_file += " file://cfg"

include grub-mender.inc
