# Class for those who want a Mender-enabled U-Boot.

inherit mender-install

EXTRA_IMAGEDEPENDS += "u-boot"

RDEPENDS_mender_append = " u-boot-fw-utils"
