inherit mender-licensing

SUB_FOLDER:arm = "arm"
SUB_FOLDER:aarch64 = "aarch64"
SUB_FOLDER:x86-64 = "x86_64"

MENDER_DEVICE_TIER:mender-update-install ?= "system"

COMPATIBLE_HOSTS = "arm|aarch64|x86_64"

RDEPENDS:${PN} = " \
    dbus-lib \
    libcrypto \
    libssl \
    libarchive \
"

FILES:${PN} = " \
    ${bindir}/mender-orchestrator \
    ${localstatedir}/lib/mender-orchestrator \
    /data/mender-orchestrator \
"

S = "${WORKDIR}/mender-orchestrator-${PV}"

do_version_check() {
    if [ ! -e ${S}/${SUB_FOLDER}/mender-orchestrator ]; then
        bbfatal "No mender-orchestrator binary found. Have you added the package to SRC_URI?"
    fi

    if ! ${@'true' if d.getVar('MENDER_DEVMODE') else 'false'}; then
        if ! strings ${S}/${SUB_FOLDER}/mender-orchestrator | grep -q "^${PV}$"; then
            bbfatal "String '${PV}' not found in binary. Is it the correct version? Check with --version."
        fi
    fi
}
addtask do_version_check after do_unpack before do_topology_file_check

do_topology_file_check() {
    if [ ! -e ${WORKDIR}/topology.yaml ]; then
        bbfatal "No topology.yaml found. Have you added the package to SRC_URI?"
    fi
}
addtask do_topology_file_check after do_version_check before do_install

do_install() {
    install -d -m 755 ${D}${bindir}
    install -m 755 ${S}/${SUB_FOLDER}/mender-orchestrator ${D}${bindir}/mender-orchestrator

    install -d -m 755 ${D}/data/mender-orchestrator
    install -d -m 755 ${D}${localstatedir}/lib/
    ln -s /data/mender-orchestrator ${D}${localstatedir}/lib/mender-orchestrator

    # mender-orchestrator-support provides a pre-made topology in the demo layer
    if [ -e ${WORKDIR}/topology.yaml ]; then
        install -m 755 ${WORKDIR}/topology.yaml ${D}/data/mender-orchestrator/topology.yaml
    fi
}
