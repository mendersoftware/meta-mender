DESCRIPTION = "Mender image artifact library"
GO_IMPORT = "github.com/mendersoftware/mender-artifact"

inherit go

S = "${WORKDIR}/git"

GO_LDFLAGS = '-ldflags="${GO_RPATH} ${GO_LINKMODE} ${GO_MENDER_LDFLAGS} -extldflags '${GO_EXTLDFLAGS}'"'

do_configure_append () {
    # Create dummy file, see https://github.com/golang/go/issues/22409
    echo "package tesseract" > ${S}/src/${GO_IMPORT}/dummy.go
}

python extract_main_version() {
    import bb.process
    workdir = '%s/src/%s' % (d.getVar('S'), d.getVar('GO_IMPORT'))
    rev, _ = bb.process.run('git describe --tags --exact-match 2>/dev/null || git rev-parse --short HEAD', cwd=workdir)
    d.appendVar("GO_MENDER_LDFLAGS", " -X main.Version=%s" % rev)
}

do_compile[prefuncs] += "extract_main_version"

BBCLASSEXTEND = "native"
