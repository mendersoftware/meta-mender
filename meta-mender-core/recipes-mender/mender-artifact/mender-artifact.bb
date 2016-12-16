DESCRIPTION = "Mender artifact information"
HOMEPAGE = "https://mender.io"
LICENSE = "Apache-2.0"
LIC_FILES_CHKSUM = "file://Apache-2.0;md5=f4a3edb2a8fe8e2ecde8062ba20b1c86"

FILESPATH = "${COMMON_LICENSE_DIR}"
SRC_URI = "file://Apache-2.0"

S = "${WORKDIR}"

inherit allarch

PV = "0.1"

do_compile() {
    if [ -z "${MENDER_ARTIFACT_NAME}" ]; then
        bberror "Need to define MENDER_ARTIFACT_NAME variable."
        exit 1
    fi

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
