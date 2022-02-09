DESCRIPTION = "Mender image artifact library"
GO_IMPORT = "github.com/mendersoftware/mender-artifact"

inherit go
inherit go-ptest

S = "${WORKDIR}/git"
B = "${WORKDIR}/build"

GOPATHDIR = "${B}/src/${GO_IMPORT}"

BBCLASSEXTEND = "native nativesdk"

do_compile() {
    # we could check out the sources at some destsuffix and use default
    # do_compile from go.bbclass, but that would prevent us from always building
    # the most recent version due to recursive expansion if SRCPV

    GOPATH=${B}:${STAGING_LIBDIR}/${TARGET_SYS}/go go env
    if grep -q "goinstall:" ${GOPATHDIR}/Makefile; then
        # New method.
        oe_runmake GOPATH=${B}:${STAGING_LIBDIR}/${TARGET_SYS}/go -C ${GOPATHDIR} V=1
    else
        # Legacy method. Remove once all recipes are using a Makefile with
        # "goinstall:" in it.
        oe_runmake GOPATH=${B}:${STAGING_LIBDIR}/${TARGET_SYS}/go -C ${GOPATHDIR} V=1 install
    fi
}

do_install() {
    install -d ${D}${bindir}

    if grep -q "goinstall:" ${GOPATHDIR}/Makefile; then
        # New method.
        oe_runmake -C ${GOPATHDIR} DESTDIR=${D} PREFIX=${prefix_native} V=1 install
    else
        # Legacy method. Remove once all recipes are using a Makefile with
        # "goinstall:" in it.

        # go cross-compilation builds are in different place than native ones.
        if [ "${BUILD_ARCH}" = "${HOST_ARCH}" ]; then
            BUILD_BIN_FOLDER=${B}/bin
        else
            BUILD_BIN_FOLDER=${B}/bin/${GOOS}_${GOARCH}
        fi

        install ${BUILD_BIN_FOLDER}/mender-artifact -m 0755 ${D}${bindir}
    fi
}
