# Class for those who want a Mender-ready device image.

inherit mender-install

OVERRIDES_append = ":menderimage"

#Make sure we are creating sdimg with all needed partitioning.
IMAGE_CLASSES += "mender-sdimg mender-artifactimg"
IMAGE_FSTYPES_append = " sdimg mender"
