FILESEXTRAPATHS_prepend := "${THISDIR}/patches:"
SRC_URI_append_mender-client-install = " file://0001-Do-not-use-metadata_csum-feature-on-ext4-by-default.patch"
