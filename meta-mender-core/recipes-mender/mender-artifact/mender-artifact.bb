DESCRIPTION = "Mender artifact information"
HOMEPAGE = "https://mender.io"
LICENSE = "Apache-2.0"

inherit allarch

PV = "0.1"

do_compile() {
    cat > ${B}/artifact_info << END
artifact_name=${MENDER_ARTIFACT_NAME}
END
}

do_install() {
    install -d ${D}${sysconfdir}/mender
    install -m 0644 -t ${D}${sysconfdir}/mender ${B}/artifact_info
}

FILES_${PN} += " \
    ${sysconfdir}/mender/artifact_info \
"
