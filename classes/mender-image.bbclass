#Add meta information to the created image
inherit mender-image-buildinfo

#Make sure we are creating sdimg with all needed partitioning.
IMAGE_CLASSES += "mender-sdimg"
IMAGE_FSTYPES ?= "tar.gz ext3 sdimg"
