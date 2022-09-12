
FILES:${PN}-doc:append = " \
    ${docdir}/mender-gateway/examples \
    ${sysconfdir}/mender/mender-gateway.conf \
"

def examples_dir_from_s_dir(d, s):
    return s.replace("mender-gateway-", "mender-gateway-examples-")

EXAMPLES = "${@examples_dir_from_s_dir(d, '${S}')}"

do_install:append() {
    cp -R --no-dereference --preserve=mode,links -v ${EXAMPLES}/* ${D}
}
