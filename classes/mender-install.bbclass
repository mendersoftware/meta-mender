#Add meta information to the created image
inherit mender-image-buildinfo
IMAGE_PREPROCESS_COMMAND += "buildinfo_mender;"

EXTRA_IMAGEDEPENDS += "u-boot u-boot-fw-utils"
PREFERRED_VERSION_u-boot = "v2015.10%"
PREFERRED_VERSION_u-boot-fw-utils = "v2015.10%"
PREFERRED_VERSION_go_cross = "1.5%"

#Add support for systemd
DISTRO_FEATURES_append = " systemd"
VIRTUAL-RUNTIME_init_manager = "systemd"
DISTRO_FEATURES_BACKFILL_CONSIDERED = "sysvinit"
VIRTUAL-RUNTIME_initscripts = ""


#Make sure we are creating sdimg with all needed partitioning.
IMAGE_CLASSES += "sdimg"
IMAGE_FSTYPES += "sdimg"

IMAGE_INSTALL_append = " u-boot-fw-utils mender"


