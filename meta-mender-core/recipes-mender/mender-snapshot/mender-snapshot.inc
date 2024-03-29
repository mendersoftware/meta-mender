DESCRIPTION = "Mender tool for creating golden-images from a given installation."
HOMEPAGE = "https://mender.io"

DEPENDS:append = " glib-2.0"
RDEPENDS:${PN} = "glib-2.0 mender-update (>= 4.0)"

B = "${WORKDIR}/build"

inherit go-mod
inherit go-ptest

GO_IMPORT = "github.com/mendersoftware/mender-snapshot"

do_compile() {
    oe_runmake \
        -C ${B}/src/${GO_IMPORT} \
        V=1
}

do_install() {
    oe_runmake \
        -C ${B}/src/${GO_IMPORT} \
        V=1 \
        prefix=${D} \
        bindir=${bindir} \
        datadir=${datadir} \
        sysconfdir=${sysconfdir} \
        install-bin
}
