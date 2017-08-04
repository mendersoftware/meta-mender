require mender-artifact.inc

SRC_URI = "git://github.com/mendersoftware/mender-artifact.git;protocol=https;branch=2.1.x"

SRCREV = "59b2c9f220271a4fedd6f7ffbec6daed32a45485"

LICENSE = "Apache-2.0"
LIC_FILES_CHKSUM = "file://LIC_FILES_CHKSUM.sha256;md5=1baf9ba39aca12f99a87a99b18440e84"

# Downprioritize this recipe in version selections.
DEFAULT_PREFERENCE = "-1"
