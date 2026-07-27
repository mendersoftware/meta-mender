inherit mender-licensing

DESCRIPTION = "Mender Delta Container Modules"
HOMEPAGE = "https://mender.io"

SUB_FOLDER:arm = "arm"
SUB_FOLDER:aarch64 = "aarch64"
SUB_FOLDER:x86-64 = "x86_64"

COMPATIBLE_HOST = "arm|aarch64|x86_64"

PACKAGES =+ "mender-delta-docker-compose"

# "lsb-ld" is needed because Yocto by default does not provide a cross platform
# dynamic linker. On x86_64 this manifests as a missing
# `/lib64/ld-linux-x86-64.so.2`.
RDEPENDS:mender-delta-docker-compose = "mender-update docker-compose docker jq lsb-ld"

FILES:mender-delta-docker-compose = " \
    ${datadir}/mender/modules/v3/delta-docker-compose \
    ${bindir}/xdelta3 \
"

do_version_check() {
    if [ ! -e ${S}/delta-docker-compose ] || [ ! -e ${S}/${SUB_FOLDER}/xdelta3 ]; then
        bbfatal "No delta-docker-compose module found. Have you added the package to SRC_URI?"
    fi
}
addtask do_version_check after do_patch before do_install

do_install() {
    install -d -m 755 ${D}${datadir}/mender/modules/v3
    install -m 755 ${S}/delta-docker-compose ${D}${datadir}/mender/modules/v3/delta-docker-compose

    install -d -m 755 ${D}${bindir}
    install -m 755 ${S}/${SUB_FOLDER}/xdelta3 ${D}${bindir}/xdelta3
}
