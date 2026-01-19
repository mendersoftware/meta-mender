inherit mender-licensing

DESCRIPTION = "Utility to flash block devices."
HOMEPAGE = "https://mender.io"

inherit pkgconfig

# Don't download the googletest source in Mender CMakefiles.txt
EXTRA_OECMAKE:append = " -DMENDER_DOWNLOAD_GTEST=NO"

inherit cmake

FILES:${PN} = " \
    ${bindir}/mender-flash \
"

DEPENDS += "googletest"

B = "${WORKDIR}/build"
