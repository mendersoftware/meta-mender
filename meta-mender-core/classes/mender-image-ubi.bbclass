# Class for those who want a Mender-ready UBI device image.

inherit mender-install

#Make sure we are creating ubimg with all needed partitioning.
IMAGE_CLASSES += " mender-ubimg"
IMAGE_FSTYPES_append = " ubimg"
