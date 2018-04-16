FILESEXTRAPATHS_prepend := "${THISDIR}/files:"

# toradex board is using 2016.11 u-boot, need to apply a patch that matches our version
SRC_URI_remove = "file://0003-Integration-of-Mender-boot-code-into-U-Boot.patch"
SRC_URI_append = " file://0003-U-Boot-pre-2017.03-integration-of-Mender-boot-code-i.patch"

# 64kB
BOOTENV_SIZE ?= "0x10000"
