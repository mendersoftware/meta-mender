LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/Apache-2.0;md5=89aea4e17d99a7cacdbeed46a0096b10"
LICENSE = "Apache-2.0"

FILES:${PN} = "${datadir}/mender/modules/v3/logger-update-module"

do_compile() {
    cat > ${B}/logger-update-module <<'EOF'
#!/bin/sh
case "$1" in
    NeedsArtifactReboot)
        echo "Yes"

        # Don't log this one, it is not related to state flow.
        ;;
    SupportsRollback)
        echo "No"

        # Don't log this one, it is not related to state flow.
        ;;
    *)
        echo "$(date +%s)" "$@" >> /data/logger-update-module.log
        ;;
esac
EOF
}

do_install() {
    install -m 755 -d ${D}${datadir}/mender/modules/v3
    install -m 755 ${B}/logger-update-module ${D}${datadir}/mender/modules/v3/logger-update-module
}
