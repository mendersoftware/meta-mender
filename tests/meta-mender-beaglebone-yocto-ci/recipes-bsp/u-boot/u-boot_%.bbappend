FILESEXTRAPATHS:prepend := "${THISDIR}/patches:"

SRC_URI:append_mender-testing-enabled = " file://reenable_uenvcmd.patch"
