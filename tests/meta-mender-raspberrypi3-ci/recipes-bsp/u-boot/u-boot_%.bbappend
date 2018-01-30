FILESEXTRAPATHS_prepend := "${THISDIR}/patches:"

# Revert patch which breaks USB storage on Raspberry Pi.
SRC_URI_append = " file://0001-Revert-usb-Only-get-64-bytes-device-descriptor-for-f.patch"
