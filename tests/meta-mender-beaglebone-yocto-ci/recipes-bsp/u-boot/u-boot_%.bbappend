FILESEXTRAPATHS_prepend := "${THISDIR}/patches:"

SRC_URI_append_mender-testing-enabled = " file://reenable_uenvcmd.patch"
