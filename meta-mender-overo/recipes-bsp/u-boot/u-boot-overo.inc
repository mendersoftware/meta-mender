FILESEXTRAPATHS_prepend_overo := "${THISDIR}/patches:"

# Overo board is using 2016.11 u-boot, need to apply a patch that matches our version
SRC_URI_remove_overo += " file://0003-Integration-of-Mender-boot-code-into-U-Boot.patch"
SRC_URI_append_overo += " file://0003-U-Boot-pre-2017.03-integration-of-Mender-boot-code-i.patch"

SRC_URI_append_overo += " file://0002-u-boot-Mender-integration-for-Overo-board.patch"

# Custom DEVICE_NAME based on upstream kernel DTB and UBoot MTD partition table
# This needs to be kept in sync with arch/arm/boot/dts/omap3-overo-base.dtsi
MENDER_MTD_UBI_DEVICE_NAME_overo = "Filesystem"

# UBoot environment on Overo boards is 128kB.
# 2 copies are maintained in the environ MTD partition
BOOTENV_SIZE_overo = "0x20000"
BOOTENV_RANGE_overo = "0x20000"
