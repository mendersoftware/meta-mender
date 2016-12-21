DESCRIPTION = "Mender image artifact library"
GO_IMPORT = "github.com/mendersoftware/mender-artifact"

inherit go
# these are fixed in oe-meta-go
GOBIN_FINAL_class-native = "${GOROOT_FINAL}/bin"
GOROOT_class-native = "${STAGING_LIBDIR_NATIVE}/go"
export GOROOT
export GOBIN_FINAL

SRC_URI = "git://github.com/mendersoftware/mender-artifact.git;protocol=https"

SRCREV = "${AUTOREV}"
PVBASE := "${PV}"
PV = "${PVBASE}+git${SRCPV}"

LICENSE = "Apache-2.0"
LIC_FILES_CHKSUM = " \
                    file://LIC_FILES_CHKSUM.sha256;md5=f4a3edb2a8fe8e2ecde8062ba20b1c86 \
                    "
S = "${WORKDIR}/git"
B = "${WORKDIR}/build"

GOPATHDIR = "${B}/src/${GO_IMPORT}"

BBCLASSEXTEND = "native"

do_compile() {
    # we could check out the sources at some destsuffix and use default
    # do_compile from go.bbclass, but that would prevent us from always building
    # the most recent version due to recursive expansion if SRCPV

    install -d ${GOPATHDIR}
    # we could also try symlinking ${S} into our fake GOPATH, however `go build...`
    # ignores symlinks in GOPATH
    rsync -av --exclude '.git' --delete ${S}/ ${GOPATHDIR}/

    GOPATH=${B}:${STAGING_LIBDIR}/${TARGET_SYS}/go go env
    if test -n "${GO_INSTALL}" ; then
       GOPATH=${B}:${STAGING_LIBDIR}/${TARGET_SYS}/go go install -v ${GO_INSTALL}
    fi
}

do_install() {
    install -d ${D}${GOROOT_FINAL}
    rsync -av \
          --exclude '*/vendor/github.com/mendersoftware/mendertesting/*.sh' \
          ${B}/ ${D}${GOROOT_FINAL}

    if test -e ${D}${GOBIN_FINAL} ; then
        install -d ${D}${bindir}
        find ${D}${GOBIN_FINAL} ! -type d -print0 | xargs -r0 mv --target-directory="${D}${bindir}"
        rmdir -p ${D}${GOBIN_FINAL} || true
        chown -R root:root ${D}${bindir}
    fi
    chown -R root:root ${D}${GOROOT_FINAL}
}
