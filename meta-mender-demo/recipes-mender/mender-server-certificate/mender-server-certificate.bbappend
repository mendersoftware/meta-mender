FILESEXTRAPATHS:prepend := "${THISDIR}/files:"
SRC_URI:append = " file://server.crt"

do_compile() {
    DEFAULT_CERT_MD5="3112d737da65df1b7314bfe0a98accbc"

    if [ "$(md5sum ${UNPACKDIR}/server.crt | awk '{ print $1 }')" = $DEFAULT_CERT_MD5 ]; then
        bbwarn "You are building with the default server certificate, which is not intended for production use"
    fi
}
