DESCRIPTION = "Mender image artifact library"
GO_IMPORT = "github.com/mendersoftware/gobinarycoverage"

inherit go
inherit go-ptest

SRC_URI = "git://${GO_IMPORT};protocol=git"
SRCREV = "${AUTOREV}"
LICENSE = "Apache-2.0"
LIC_FILES_CHKSUM = "file://src/${GO_IMPORT}/LICENSE;md5=86d3f3a95c324c9479bd8986968f4327"

BBCLASSEXTEND = "native nativesdk"
