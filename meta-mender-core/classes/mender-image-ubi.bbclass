# THIS IS HIGHLY EXPERIMENTAL AND COMPLETELY UNSUPPORTED! DO NOT EXPECT MENDER
# TO WORK IF YOU INCLUDE THIS CLASS. THIS IS ONLY FOR PEOPLE THAT WANT TO HELP
# AND DEVELOP UBIFS SUPPORT IN MENDER.

# Class for those who want a Mender-ready UBI device image.

inherit mender-install

#Make sure we are creating ubimg with all needed partitioning.
IMAGE_CLASSES += " mender-ubimg"
IMAGE_FSTYPES_append = " ubimg"
