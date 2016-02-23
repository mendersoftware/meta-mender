
EXTRA_IMAGEDEPENDS += "u-boot u-boot-fw-utils"

#Make sure we are creating sdimg with all needed partitioning.
IMAGE_CLASSES += "sdimg"
IMAGE_FSTYPES += "sdimg"

IMAGE_INSTALL_append = " u-boot-fw-utils mender"

