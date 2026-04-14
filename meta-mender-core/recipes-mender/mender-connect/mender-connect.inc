inherit mender-licensing

DESCRIPTION = "Mender add-on for remote terminal access."
HOMEPAGE = "https://mender.io"

DEPENDS:append = " glib-2.0"
RDEPENDS:${PN} = "glib-2.0 mender-auth"

MENDER_CONNECT_SHELL ??= "/bin/sh"
MENDER_CONNECT_USER ??= "nobody"
SYSTEMD_AUTO_ENABLE ?= "enable"
SYSTEMD_SERVICE:${PN} = "mender-connect.service"

B = "${WORKDIR}/build"

inherit go-mod
inherit go-ptest
inherit pkgconfig
inherit systemd

GO_IMPORT = "github.com/mendersoftware/mender-connect"

# Prefer static linkage (golang's default)
GO_LINKSHARED = ""

python do_prepare_mender_connect_conf() {
    import json

    mender_connect_conf = {}
    # If a mender-connect.conf has been provided in SRC_URI, merge contents
    src_conf = os.path.join(d.getVar("UNPACKDIR"), "mender-connect.conf")
    if os.path.exists(src_conf):
        with open(src_conf) as fd:
            mender_connect_conf = json.load(fd)

    if "ShellCommand" not in mender_connect_conf:
        mender_connect_conf["ShellCommand"] = d.getVar("MENDER_CONNECT_SHELL")

    if "User" not in mender_connect_conf:
        mender_connect_conf["User"] = d.getVar("MENDER_CONNECT_USER")

    dst_conf = os.path.join(d.getVar("B"), "mender-connect.conf")
    with open(dst_conf, "w") as fd:
        json.dump(mender_connect_conf, fd, indent=4, sort_keys=True)

}
addtask do_prepare_mender_connect_conf after do_compile before do_install
do_prepare_mender_connect_conf[vardeps] = " \
    MENDER_CONNECT_SHELL \
    MENDER_CONNECT_USER \
"

# Set the version of mender-connect by passing it as an extra ldflag to go.bbclass
# This is equivalent to how it's set in the Makefile
GO_EXTRA_LDFLAGS:append = "-X github.com/mendersoftware/mender-connect/config.Version=$(git describe --tags --dirty --exact-match 2>/dev/null || git rev-parse --short HEAD)"

do_install:append() {
    # Install configuration
    mkdir -p ${D}/${sysconfdir}/mender
    install -m 0600 ${B}/mender-connect.conf ${D}/${sysconfdir}/mender/mender-connect.conf
}

do_install:append:mender-systemd() {
    # Install systemd service
    install -m 755 -d ${D}${systemd_unitdir}/system
    install -m 0644 ${B}/src/${GO_IMPORT}/support/mender-connect.service ${D}${systemd_unitdir}/system/
}

FILES:${PN}:append = "\
    ${systemd_unitdir}/system/mender-connect.service \
"
