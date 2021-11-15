FILESEXTRAPATHS:prepend := "${THISDIR}/patches:"

SRC_URI:append:mender-testing-enabled = " file://reenable_uenvcmd.patch"
