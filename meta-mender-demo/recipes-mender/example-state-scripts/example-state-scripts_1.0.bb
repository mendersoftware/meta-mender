FILESEXTRAPATHS_prepend := "${THISDIR}/files:"

SRC_URI = "file://example-script;subdir=${PN}-${PV} \
          file://LICENSE;subdir=${PN}-${PV} \
          "

LICENSE = "Apache-2.0"
LIC_FILES_CHKSUM = "file://LICENSE;md5=e3fc50a88d0a364313df4b21ef20c29e"

inherit mender-state-scripts

do_compile() {
    cp example-script ${MENDER_STATE_SCRIPTS_DIR}/Idle_Enter_00
    cp example-script ${MENDER_STATE_SCRIPTS_DIR}/Sync_Enter_10
    cp example-script ${MENDER_STATE_SCRIPTS_DIR}/Sync_Leave_90
    cp example-script ${MENDER_STATE_SCRIPTS_DIR}/ArtifactInstall_Enter_00
    cp example-script ${MENDER_STATE_SCRIPTS_DIR}/ArtifactInstall_Leave_99
    cp example-script ${MENDER_STATE_SCRIPTS_DIR}/ArtifactReboot_Leave_50
    cp example-script ${MENDER_STATE_SCRIPTS_DIR}/ArtifactCommit_Enter_50
    cp example-script ${MENDER_STATE_SCRIPTS_DIR}/ArtifactCommit_Leave_50
}
