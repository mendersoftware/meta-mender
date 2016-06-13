inherit mender-install

EXTRA_IMAGEDEPENDS += "u-boot"

RDEPENDS_mender_append = " u-boot-fw-utils"
