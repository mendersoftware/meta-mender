# Override version check to allow missing topology.yaml in SRC_URI
# The demo layer provides a pre-defined topology via mender-orchestrator-support
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

