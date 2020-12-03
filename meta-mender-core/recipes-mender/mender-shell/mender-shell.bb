DESCRIPTION = "Mender program for remote terminal access."
HOMEPAGE = "https://mender.io"

SRC_URI = "git://github.com/mendersoftware/mender-shell.git;protocol=https;branch=master"

# See: https://www.yoctoproject.org/docs/2.5.1/dev-manual/dev-manual.html#automatically-incrementing-a-binary-package-revision-number
SRCREV = "${AUTOREV}"
PV = "0.1+git${SRCPV}"

# DO NOT change the checksum here without make sure that ALL licenses (including
# dependencies) are included in the LICENSE variable below. Note that for
# releases, we must check the LIC_FILES_CHKSUM.sha256 file, not the LICENSE
# file.
LICENSE = "Apache-2.0 & BSD-2-Clause & BSD-3-Clause & ISC & MIT"
LIC_FILES_CHKSUM = "file://src/${GO_IMPORT}/LICENSE;md5=7fd64609fe1bce47db0e8f6e3cc6a11d"

inherit go-mod
inherit go-ptest

DEPENDS_append = " pkgconfig-native glib-2.0"
RDEPENDS_${PN} = "glib-2.0"

GO_IMPORT = "github.com/mendersoftware/mender-shell"

do_compile() {
    oe_runmake V=1
}

do_install() {
    oe_runmake \
        -C ${B}/src/${GO_IMPORT} \
        V=1 \
        prefix=${D} \
        bindir=${bindir} \
        datadir=${datadir} \
        sysconfdir=${sysconfdir} \
        systemd_unitdir=${systemd_unitdir} \
        install-bin \
        install-systemd
}

inherit systemd

SYSTEMD_AUTO_ENABLE ?= "enable"

FILES_${PN}_append += "\
    ${systemd_unitdir}/system/mender-shell.service \
"
