
EXTRA_IMAGEDEPENDS += "u-boot u-boot-fw-utils"

#Make sure we are creating sdimg with all needed partitioning.
IMAGE_CLASSES += "sdimg"
IMAGE_FSTYPES += "sdimg"

IMAGE_INSTALL_append = " u-boot-fw-utils mender"


#CORE_IMAGE_BASE_INSTALL += "westonas weston-init weston-examples gtk+3-demo clutter-1.0-examples"



