FILESEXTRAPATHS:prepend:mender-systemd-boot := "${THISDIR}/files:"

SRC_URI:append:mender-systemd-boot := "\
                                      file://systemd-boot-slotconfig.patch \
                                      "
