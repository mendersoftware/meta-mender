DESCRIPTION = "Mender image artifact library"
GO_IMPORT = "github.com/mendersoftware/mender-artifact"

inherit go

S = "${WORKDIR}/git"
B = "${WORKDIR}/build"

GOPATHDIR = "${B}/src/${GO_IMPORT}"

DEPENDS_append += " rsync-native"

BBCLASSEXTEND = "native"

do_compile() {
    # we could check out the sources at some destsuffix and use default
    # do_compile from go.bbclass, but that would prevent us from always building
    # the most recent version due to recursive expansion if SRCPV

    install -d ${GOPATHDIR}
    # we could also try symlinking ${S} into our fake GOPATH, however `go build...`
    # ignores symlinks in GOPATH
    rsync -av --delete ${S}/ ${GOPATHDIR}/

    GOPATH=${B}:${STAGING_LIBDIR}/${TARGET_SYS}/go go env
    if test -n "${GO_INSTALL}" ; then
       oe_runmake GOPATH=${B}:${STAGING_LIBDIR}/${TARGET_SYS}/go -C ${GOPATHDIR} V=1 install
    fi
}

do_install() {
    install -d ${D}${bindir}
    install ${B}/bin/mender-artifact -m 0755 ${D}${bindir}
}
