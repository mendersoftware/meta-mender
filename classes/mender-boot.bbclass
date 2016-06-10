inherit mender-install

EXTRA_IMAGEDEPENDS += "u-boot u-boot-fw-utils"
PREFERRED_VERSION_u-boot = "v2015.10%"
PREFERRED_VERSION_u-boot-fw-utils = "v2015.10%"

IMAGE_INSTALL_append = " u-boot-fw-utils"
