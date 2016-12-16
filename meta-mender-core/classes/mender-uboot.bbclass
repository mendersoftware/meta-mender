# Class for those who want a Mender-enabled U-Boot.

inherit mender-install

EXTRA_IMAGEDEPENDS += "u-boot"
PACKAGECONFIG_append_pn-mender = " u-boot"

def mender_mb2bytes(mb):
    return mb * 1024 * 1024

MENDER_UBOOT_ENV_STORAGE_DEVICE_OFFSET ?= "${@mender_mb2bytes(${MENDER_PARTITION_ALIGNMENT_MB})}"
