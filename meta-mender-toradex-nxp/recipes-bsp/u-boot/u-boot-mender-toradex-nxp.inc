FILESEXTRAPATHS_prepend_vf := "${THISDIR}/files:"

BOOTENV_SIZE_vf ?= "0x20000"

SRC_URI_append_vf = " file://0001-configs-colibri_vf-adjust-for-Mender-requirements.patch"
SRC_URI_append_vf = " file://0002-configs-colibri_vf-increase-SYS_MALLOC_LEN-to-8-MB.patch"
SRC_URI_append_vf = " file://0003-colibri_vf-disable-FIT-image-enable-UBIFS.patch"
