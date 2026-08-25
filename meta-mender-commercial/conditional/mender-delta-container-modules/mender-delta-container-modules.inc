inherit mender-licensing

DESCRIPTION = "Mender Delta Container Modules"
HOMEPAGE = "https://mender.io"

PACKAGES =+ "mender-delta-docker-compose"

RDEPENDS:mender-delta-docker-compose = "mender-update docker-compose docker jq xdelta3"

FILES:mender-delta-docker-compose = " \
    ${datadir}/mender/modules/v3/delta-docker-compose \
"

do_version_check() {
    if [ ! -e ${S}/delta-docker-compose ]; then
        bbfatal "No delta-docker-compose module found. Have you added the package to SRC_URI?"
    fi
}
addtask do_version_check after do_patch before do_install

do_install() {
    install -d -m 755 ${D}${datadir}/mender/modules/v3
    install -m 755 ${S}/delta-docker-compose ${D}${datadir}/mender/modules/v3/delta-docker-compose
}
