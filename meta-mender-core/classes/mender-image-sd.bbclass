# Class for those who want a Mender-ready device image.

inherit mender-install

#Make sure we are creating sdimg with all needed partitioning.
IMAGE_CLASSES += "mender-sdimg"
IMAGE_FSTYPES_append = " sdimg"
