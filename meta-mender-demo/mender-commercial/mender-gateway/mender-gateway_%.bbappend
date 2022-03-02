
FILES_${PN}-doc_append = " \
    ${docdir}/mender-gateway/examples \
    ${sysconfdir}/mender/ \
"

def examples_dir_from_s_dir(d, s):
    return s.replace("mender-gateway-", "mender-gateway-examples-")

EXAMPLES = "${@examples_dir_from_s_dir(d, '${S}')}"

do_install_append() {
    install -d -m 755 ${D}${docdir}/mender-gateway/examples/cert
    install -m 0600 ${EXAMPLES}/examples/cert/private.key ${D}${docdir}/mender-gateway/examples/cert/private.key
    install -m 0600 ${EXAMPLES}/examples/cert/cert.crt ${D}${docdir}/mender-gateway/examples/cert/cert.crt
    install -m 0600 ${EXAMPLES}/examples/mender-gateway.conf ${D}${docdir}/mender-gateway/examples/mender-gateway.conf
    install -d -m 755 ${D}${sysconfdir}/mender
    ln -s ${docdir}/mender-gateway/examples/mender-gateway.conf ${D}${sysconfdir}/mender/mender-gateway.conf
}
