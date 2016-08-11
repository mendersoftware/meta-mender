GO_IMPORT_BASE = "github.com/bmatsuo/lmdb-go"
GO_IMPORT = "${GO_IMPORT_BASE}/lmdb"
DEST_SRC = "src/${GO_IMPORT_BASE}"

inherit go

LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${DEST_SRC}/LICENSE.mdb.md;md5=153d07ef052c4a37a8fac23bc6031972 \
                    file://${DEST_SRC}/LICENSE.md;md5=4735f81f41df64865d24bf38e42595da \
                    "
S = "${WORKDIR}/git"
# checkout under WORKDIR into a directory structure that resembles GOPATH
SRC_URI = "git://github.com/bmatsuo/lmdb-go.git;destsuffix=git/${DEST_SRC} \
           file://0001-lmdb-use-31-bit-lengths-when-on-32-bit-architectures.patch;patchdir=${DEST_SRC} \
           "

SRCREV = "d98d6a5868d62ba48850ff46066e180b77ed7934"
PV = "1.6.0+git${SRCPV}"

export CGO_ENABLED = "1"
export CGO_CFLAGS = "${CFLAGS} --sysroot=${STAGING_DIR_TARGET}"
export CGO_LDFLAGS = "${LDFLAGS} --sysroot=${STAGING_DIR_TARGET}"

do_go_compile() {
    GOPATH=${S}:${STAGING_LIBDIR}/${TARGET_SYS}/go go env
    GOPATH=${S}:${STAGING_LIBDIR}/${TARGET_SYS}/go go install -v -x ${GO_IMPORT}/...
}

do_install_append() {
    # do_go_install untars a built ${S} into a staging dir, performs some
    # cleanups, then tars the staging and it into ${D}, unfortunately polluting
    # ${D} with files that may have not been removed by the cleanup phase

    # remove files from the original repository that are not Go source code
    find ${D}${GOSRC_FINAL} -type f -not \( \
         -name '*.go' -o \
         -name '*.h' -o \
         -name '*.c' \
         \) -print0 | \
         xargs -r0 rm -f

    # there's a PR to oe-meta-go with that removes quilt patch dirs:
    # https://github.com/mem/oe-meta-go/pull/13 until that's merged we have to
    # do it ourselves
    find ${D}${GOSRC_FINAL} -type d -name '.pc' -o -name 'patches' | \
         xargs -r rm -rf

    # make sure that the user is correct (do_install is executed under fakeroot)
    chown -R root:root ${D}${GOROOT_FINAL}
}

FILES_${PN} += "${GOBIN_FINAL}/*"

# add *.go sources
FILES_${PN}-staticdev += "\
    ${GOSRC_FINAL}/${GO_IMPORT_BASE}/*.go \
    ${GOSRC_FINAL}/${GO_IMPORT_BASE}/internal \
    ${GOSRC_FINAL}/${GO_IMPORT_BASE}/exp \
    ${GOSRC_FINAL}/${GO_IMPORT_BASE}/cmd \
    "
# add all prebuilt *.a
FILES_${PN}-staticdev += "${GOPKG_FINAL}/${GO_IMPORT_BASE}"
