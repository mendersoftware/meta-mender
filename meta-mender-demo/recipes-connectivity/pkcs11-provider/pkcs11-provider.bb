LICENSE = "Apache-2.0"
LIC_FILES_CHKSUM = "file://COPYING;md5=b53b787444a60266932bd270d1cf2d45 \
                    file://LICENSES/Apache-2.0.txt;md5=3b83ef96387f14655fc854ddc3c6bd57"

SRC_URI = "git://github.com/latchset/pkcs11-provider;protocol=https;branch=main"

PV = "0.5+git${SRCPV}"
SRCREV = "7d8b369dcd9e4b72695404e4bbd9106f1436a55f"

S = "${WORKDIR}/git"

DEPENDS:append = " openssl p11-kit autoconf-archive"

inherit pkgconfig meson

FILES:${PN} =+ "${libdir}/ossl-modules/pkcs11.so"
