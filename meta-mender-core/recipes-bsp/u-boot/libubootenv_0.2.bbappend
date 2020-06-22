FILESEXTRAPATHS_prepend := "${THISDIR}/patches:"

SRC_URI_append_mender-uboot = " file://0001-Restore-ability-to-feed-script-file-via-stdin-using-.patch"
