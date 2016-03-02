
EXTRA_IMAGEDEPENDS += "u-boot u-boot-fw-utils"
PREFERRED_VERSION_u-boot = "v2015.10%"
PREFERRED_VERSION_u-boot-fw-utils = "v2015.10%"
PREFERRED_VERSION_go_cross = "1.5%"


#Make sure we are creating sdimg with all needed partitioning.
IMAGE_CLASSES += "sdimg"
IMAGE_FSTYPES += "sdimg"

IMAGE_INSTALL_append = " u-boot-fw-utils mender"

