# Recipe to provide grub-editenv by itself, for configurations where the
# upstream grub recipe doesn't work. A lot of the configuration and patches in
# here are taken from the upstream recipe.

FILESEXTRAPATHS_prepend := "${THISDIR}/patches:"

LICENSE = "GPLv3"
LIC_FILES_CHKSUM = "file://COPYING;md5=d32239bcb673463ab874e80d47fae504"

SRC_URI = "https://ftp.gnu.org/gnu/grub/grub-${PV}.tar.gz \
           file://gcc8.patch \
           file://0001-configure-Disable-soft-float-workaround.patch"
SRC_URI[md5sum] = "1116d1f60c840e6dbd67abbc99acb45d"
SRC_URI[sha256sum] = "660ee136fbcee08858516ed4de2ad87068bfe1b6b8b37896ce3529ff054a726d"

S = "${WORKDIR}/grub-${PV}"

PROVIDES = "grub-editenv"
RPROVIDES_${PN} = "grub-editenv"

inherit autotools gettext texinfo

DEPENDS = "flex-native bison-native"

EXTRA_OECONF = "--with-platform=efi \
                --disable-grub-mkfont \
                --program-prefix="" \
                --enable-liblzma=no \
                --enable-libzfs=no \
                --enable-largefile \
"

do_configure_prepend() {
	# The grub2 configure script uses variables such as TARGET_CFLAGS etc
	# for its own purposes. Remove the OE versions from the environment to
	# avoid conflicts.
	unset TARGET_CPPFLAGS TARGET_CFLAGS TARGET_CXXFLAGS TARGET_LDFLAGS
	( cd ${S}
	${S}/autogen.sh )
}

do_compile() {
    oe_runmake -C grub-core/gnulib
    oe_runmake grub-editenv
}

do_install() {
    install -m 755 -d ${D}${bindir}
    install -m 755 grub-editenv ${D}${bindir}/
}
