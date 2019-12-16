include grub-mender-grubenv.inc

SRC_URI = "git://github.com/mendersoftware/grub-mender-grubenv;protocol=https;branch=pr_10"

SRCREV = "b33bb7685454345f8f80da27b7447bdc59e9db55"
PV = "1.3.0+git${SRCREV}"

LICENSE = "Apache-2.0"
LIC_FILES_CHKSUM = "file://LICENSE;md5=a63d325b69180ec25a59e045c06ec468"
