DESCRIPTION = "Mender state-script to update firmware files on Raspberry Pi boards"
LICENSE = "Apache-2.0"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/Apache-2.0;md5=89aea4e17d99a7cacdbeed46a0096b10"

inherit mender-state-scripts

SRC_URI = "file://ArtifactInstall_Leave_50.in"

do_deploy() {
    sed -e 's#@@MENDER_ROOTFS_PART_A@@#'"${MENDER_ROOTFS_PART_A}"'#' \
        -e 's#@@MENDER_ROOTFS_PART_B@@#'"${MENDER_ROOTFS_PART_B}"'#' \
        "${WORKDIR}/ArtifactInstall_Leave_50.in" > "${WORKDIR}/ArtifactInstall_Leave_50"
    cp ${WORKDIR}/ArtifactInstall_Leave_50 ${MENDER_STATE_SCRIPTS_DIR}/ArtifactInstall_Leave_50
}

ALLOW_EMPTY:${PN} = "1"
