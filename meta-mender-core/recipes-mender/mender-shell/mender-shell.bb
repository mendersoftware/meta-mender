DESCRIPTION = "Mender program for remote terminal access."
HOMEPAGE = "https://mender.io"

SRC_URI = "git://github.com/mendersoftware/mender-shell.git;protocol=https;branch=master"

# See: https://www.yoctoproject.org/docs/2.5.1/dev-manual/dev-manual.html#automatically-incrementing-a-binary-package-revision-number
SRCREV = "${AUTOREV}"
PV = "0.1+git${SRCPV}"

LICENSE = "Apache-2.0 & BSD-2-Clause & BSD-3-Clause & ISC & MIT"
LIC_FILES_CHKSUM = "file://src/${GO_IMPORT}/LIC_FILES_CHKSUM.sha256;md5=98fb11e1874b0aef96c1bac976ca6aa3"

inherit go-mod
inherit go-ptest

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

FILES_${PN}_append-mender-shell-systemd += "\
    ${systemd_unitdir}/system/mender-shell.service \
"
