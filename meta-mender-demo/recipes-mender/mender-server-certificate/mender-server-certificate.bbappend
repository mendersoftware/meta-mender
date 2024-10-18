FILESEXTRAPATHS:prepend := "${THISDIR}/files:"
SRC_URI:append = " file://server.crt"

do_compile() {
    DEFAULT_CERT_MD5="82eeb8af6b3bea4ab114ae92d24fa1c7"

    if [ "$(md5sum ${WORKDIR}/server.crt | awk '{ print $1 }')" = $DEFAULT_CERT_MD5 ]; then
        bbwarn "You are building with the default server certificate, which is not intended for production use"
    fi
}
