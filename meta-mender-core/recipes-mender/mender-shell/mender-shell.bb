DESCRIPTION = "Mender add-on for remote terminal access."
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

DEPENDS_append = " glib-2.0"
RDEPENDS_${PN} = "glib-2.0"

MENDER_SERVER_URL ?= "https://docker.mender.io"
MENDER_SHELL_USER ??= "nobody"
SYSTEMD_AUTO_ENABLE ?= "enable"

B = "${WORKDIR}/build"

inherit go
inherit pkgconfig
inherit systemd

GO_IMPORT = "github.com/mendersoftware/mender-shell"

do_compile() {
    oe_runmake \
        -C ${B}/src/${GO_IMPORT} \
        V=1
}

python do_prepare_mender_shell_conf() {
    import json

    mender_shell_conf = {}
    # If a mender-shell.conf has been provided in SRC_URI, merge contents
    src_conf = os.path.join(d.getVar("WORKDIR"), "mender-shell.conf")
    if os.path.exists(src_conf):
        with open(src_conf) as fd:
            mender_shell_conf = json.load(fd)

    if "ServerURL" not in mender_shell_conf:
        mender_shell_conf["ServerURL"] = d.getVar("MENDER_SERVER_URL")

    if "User" not in mender_shell_conf:
        mender_shell_conf["User"] = d.getVar("MENDER_SHELL_USER")

    dst_conf = os.path.join(d.getVar("B"), "mender-shell.conf")
    with open(dst_conf, "w") as fd:
        json.dump(mender_shell_conf, fd, indent=4, sort_keys=True)

}
addtask do_prepare_mender_shell_conf after do_compile before do_install
do_prepare_mender_shell_conf[vardeps] = " \
    MENDER_SERVER_URL \
    MENDER_SHELL_USER \
"

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

    # install configuration
    mkdir -p  ${D}/${sysconfdir}/mender
    install -m 0600 ${B}/mender-shell.conf ${D}/${sysconfdir}/mender/mender-shell.conf
}

FILES_${PN}_append += "\
    ${systemd_unitdir}/system/mender-shell.service \
"
