DESCRIPTION = "Mender self-signed server certificate"
HOMEPAGE = "https://mender.io"
LICENSE = "Apache-2.0"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/Apache-2.0;md5=89aea4e17d99a7cacdbeed46a0096b10"

DEPENDS = "ca-certificates"
RDEPENDS:${PN} = "ca-certificates"

S = "${WORKDIR}/sources"
UNPACKDIR = "${S}"

localdatadir = "${prefix}/local/share"

inherit allarch

PV = "0.1"

do_install() {
    if [ ! -f ${UNPACKDIR}/server.crt ]; then
        bbfatal "No server server.crt found in SRC_URI"
    fi

    install -m 0755 -d ${D}${localdatadir}/ca-certificates/mender

    # MEN-4580: Multiple certificates in one file are necessary to split in
    # order for `update-ca-certificates` to produce a hashed symlink to them,
    # which is required by some programs, such as curl.
    if [ $(fgrep 'BEGIN CERTIFICATE' ${UNPACKDIR}/server.crt | wc -l) -gt 1 ]; then
        certnum=1
        while read LINE; do
            if [ -z "$cert" ] || echo "$LINE" | fgrep -q 'BEGIN CERTIFICATE'; then
                cert=${D}${localdatadir}/ca-certificates/mender/server-$certnum.crt
                rm -f $cert
                touch $cert
                chmod 0444 $cert
                certnum=$(expr $certnum + 1)
            fi
            echo "$LINE" >> $cert
        done < ${UNPACKDIR}/server.crt
    else
        install -m 0444 ${UNPACKDIR}/server.crt ${D}${localdatadir}/ca-certificates/mender/server.crt
    fi
}

FILES:${PN} += " \
    ${localdatadir}/ca-certificates/mender/ \
"

pkg_postinst:${PN} () {
    SYSROOT="$D" $D${sbindir}/update-ca-certificates
}
