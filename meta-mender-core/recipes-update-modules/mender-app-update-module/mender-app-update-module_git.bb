DESCRIPTION = "Mender Application Update Module for supporting containerized application updates on devices including related tools."

HOMEPAGE = "https://mender.io"
LICENSE = "Apache-2.0"
LIC_FILES_CHKSUM = "file://LICENSE;md5=b4b4cfdaea6d61aa5793b92efd42e081"

SRC_URI = "git://github.com/mendersoftware/app-update-module;branch=master;protocol=https"

SRCREV = "15025d9f1e21eafcbf1325b2a5034b2606e1d719"

S = "${WORKDIR}/git"

RDEPENDS:${PN} = "jq mender-update xdelta3"

PACKAGECONFIG ?= ""
PACKAGECONFIG[docker-compose] = ",,,docker-compose"
PACKAGECONFIG[k3s] = ",,,packagegroup-k3s-node"
PACKAGECONFIG[k8s] = ",,,kubectl"

inherit allarch

do_configure[noexec] = "1"

do_compile() {
    if ! ${@bb.utils.contains('PACKAGECONFIG', 'docker-compose', 'true', 'false', d)} && \
       ! ${@bb.utils.contains('PACKAGECONFIG', 'k3s', 'true', 'false', d)} && \
       ! ${@bb.utils.contains('PACKAGECONFIG', 'k8s', 'true', 'false', d)}; then
        bbwarn "PACKAGECONFIG for mender-app-update-module is empty or invalid. Please specify either 'docker-compose', 'k3s' or 'k8s' unless you know what you are doing."
    fi
}

do_install:class-target() {
    # install the Application Update Module
    install -d ${D}/${datadir}/mender/app-modules/v1
    install -d ${D}/${datadir}/mender/modules/v3
    install -m 755 ${S}/src/app ${D}/${datadir}/mender/modules/v3/app

    # install the configuration files
    install -d ${D}/${sysconfdir}/mender
    install -m 755 ${S}/conf/mender-app.conf ${D}/${sysconfdir}/mender/mender-app.conf

    # install the Docker Compose Module
    if ${@bb.utils.contains('PACKAGECONFIG', 'docker-compose', 'true', 'false', d)}; then
        install -m 755 ${S}/src/app-modules/docker-compose ${D}/${datadir}/mender/app-modules/v1/docker-compose
        install -m 755 ${S}/conf/mender-app-docker-compose.conf ${D}/${sysconfdir}/mender/mender-app-docker-compose.conf
    fi

    # install the K8S Module
    if ${@bb.utils.contains('PACKAGECONFIG', 'k3s', 'true', 'false', d)} || ${@bb.utils.contains('PACKAGECONFIG', 'k8s', 'true', 'false', d)}; then
        install -m 755 ${S}/src/app-modules/k8s ${D}/${datadir}/mender/app-modules/v1/k8s
        install -m 755 ${S}/conf/mender-app-k8s.conf ${D}/${sysconfdir}/mender/mender-app-k8s.conf
    fi
}

do_install:class-native() {
    install -d ${D}/${bindir}
    install -m 755 ${S}/gen/app-gen ${D}/${bindir}/app-gen
}

FILES:${PN} += "${datadir}/mender/modules/v3/app"
FILES:${PN} += "${datadir}/mender/app-modules/v1"
FILES:${PN} += "${@bb.utils.contains('PACKAGECONFIG', 'docker-compose', '${datadir}/mender/app-modules/v1/docker-compose', '', d)}"
FILES:${PN} += "${@bb.utils.contains('PACKAGECONFIG', 'k3s', '${datadir}/mender/app-modules/v1/k8s', '', d)}"
FILES:${PN} += "${@bb.utils.contains('PACKAGECONFIG', 'k8s', '${datadir}/mender/app-modules/v1/k8s', '', d)}"

FILES:${PN}-class-native += "${bindir}/app-gen"

BBCLASSEXTEND = "native"
