FILESEXTRAPATHS:prepend := "${THISDIR}/files:"

SRC_URI:mender-systemd-boot += "file://systemd-boot-slotconfig.patch"
