FILESEXTRAPATHS_prepend := "${THISDIR}/files:"

SRC_URI = " \
          file://wait-for-timesync;subdir=${PN}-${PV} \
          file://LICENSE;subdir=${PN}-${PV} \
          "

LICENSE = "Apache-2.0"
LIC_FILES_CHKSUM = "file://LICENSE;md5=e3fc50a88d0a364313df4b21ef20c29e"

inherit mender-state-scripts

ALLOW_EMPTY_${PN} = "1"

do_compile() {
    cp wait-for-timesync ${MENDER_STATE_SCRIPTS_DIR}/ArtifactCommit_Enter_10_wait-for-timesync
}
