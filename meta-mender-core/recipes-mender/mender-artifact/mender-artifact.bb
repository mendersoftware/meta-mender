DESCRIPTION = "Mender artifact information"
HOMEPAGE = "https://mender.io"
LICENSE = "Apache-2.0"

inherit allarch

PV = "0.1"

do_compile() {
    echo "# populate this file with build info" > ${B}/artifact-info
}

do_install() {
    install -d ${D}${sysconfdir}/mender
    install -t ${D}${sysconfdir}/mender ${B}/artifact-info
    ln -s artifact-info ${D}${sysconfdir}/mender/build_mender
}

FILES_${PN} += " \
    ${sysconfdir}/mender/artifact-info \
    ${sysconfdir}/mender/build_mender \
"
