include grub-mender-grubenv.inc

SRC_URI = "git://github.com/mendersoftware/grub-mender-grubenv;protocol=https;branch=grub-debug-prompt"

SRCREV = "bf2387b1e95b106a09cdf6bc801817bd5bd39d7e"
PV = "1.3.0+git${SRCREV}"

LICENSE = "Apache-2.0"
LIC_FILES_CHKSUM = "file://LICENSE;md5=a63d325b69180ec25a59e045c06ec468"
