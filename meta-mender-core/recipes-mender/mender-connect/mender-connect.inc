DESCRIPTION = "Mender add-on for remote terminal access."
HOMEPAGE = "https://mender.io"

DEPENDS_append = " glib-2.0"
RDEPENDS_${PN} = "glib-2.0 mender-client (>= 2.5)"

MENDER_SERVER_URL ?= "https://docker.mender.io"
MENDER_CONNECT_SHELL ??= "/bin/sh"
MENDER_CONNECT_USER ??= "nobody"
SYSTEMD_AUTO_ENABLE ?= "enable"
SYSTEMD_SERVICE_${PN} = "mender-connect.service"

B = "${WORKDIR}/build"

inherit go
inherit go-ptest
inherit pkgconfig
inherit systemd

GO_IMPORT = "github.com/mendersoftware/mender-connect"

do_compile() {
    oe_runmake \
        -C ${B}/src/${GO_IMPORT} \
        V=1
}

python do_prepare_mender_connect_conf() {
    import json

    mender_connect_conf = {}
    # If a mender-connect.conf has been provided in SRC_URI, merge contents
    src_conf = os.path.join(d.getVar("WORKDIR"), "mender-connect.conf")
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
    MENDER_SERVER_URL \
    MENDER_CONNECT_SHELL \
    MENDER_CONNECT_USER \
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
    install -m 0600 ${B}/mender-connect.conf ${D}/${sysconfdir}/mender/mender-connect.conf
}

FILES_${PN}_append += "\
    ${systemd_unitdir}/system/mender-connect.service \
"
