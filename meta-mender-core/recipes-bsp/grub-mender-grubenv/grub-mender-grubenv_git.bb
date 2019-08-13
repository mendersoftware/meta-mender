include grub-mender-grubenv.inc

SRC_URI = "git://github.com/mendersoftware/grub-mender-grubenv;protocol=https;branch=master"

SRCREV = "444738fc26dccc68b1efaf7ab566f0dafff0bed1"
PV = "1.3.0+git${SRCREV}"

LICENSE = "Apache-2.0"
LIC_FILES_CHKSUM = "file://LICENSE;md5=a63d325b69180ec25a59e045c06ec468"
