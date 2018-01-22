FILESEXTRAPATHS_prepend_orangepi := "${THISDIR}/patches:"

SRC_URI_append_orangepi = " file://default-gcc.patch"
