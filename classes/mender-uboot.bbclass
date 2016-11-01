# Class for those who want a Mender-enabled U-Boot.

inherit mender-install

# u-boot environment file to be stored on boot partition
IMAGE_BOOT_ENV_FILE ?= "uboot.env"
IMAGE_BOOT_FILES_append = " ${IMAGE_BOOT_ENV_FILE}"

EXTRA_IMAGEDEPENDS += "u-boot"

DEPENDS_mender_append = " u-boot u-boot-fw-utils"
RDEPENDS_mender_append = " u-boot u-boot-fw-utils"
