# The Go in Yocto LTS releases can be older than what go.mod requires
python mender_go_version_check() {
    import re

    with open(d.expand("${B}/src/${GO_IMPORT}/go.mod")) as f:
        need = re.search(r"^go (\S+)", f.read(), re.M).group(1)
    out, _ = bb.process.run(d.expand("GOTOOLCHAIN=local ${GO} env GOVERSION"))
    have = re.match(r"go(\S+)", out).group(1)
    if bb.utils.vercmp_string_op(have, need, "<"):
        bb.fatal(d.expand("${BPN} needs Go >= %s, but this build has Go %s. Add or update the "
                          "meta-lts-mixins layer (${LAYERSERIES_CORENAMES}/go branch): "
                          "https://git.yoctoproject.org/meta-lts-mixins") % (need, have))
}
do_compile[prefuncs] += "mender_go_version_check"
