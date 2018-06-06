# Class to create the "dataimg" type, which contains the data partition as a raw
# filesystem.

IMAGE_CMD_dataimg() {
    dd if=/dev/zero of="${WORKDIR}/data.${ARTIFACTIMG_FSTYPE}" count=0 bs=1M seek=${MENDER_DATA_PART_SIZE_MB}
    mkfs.${ARTIFACTIMG_FSTYPE} -F "${WORKDIR}/data.${ARTIFACTIMG_FSTYPE}" -d "${IMAGE_ROOTFS}/data" -L data
    install -m 0644 "${WORKDIR}/data.${ARTIFACTIMG_FSTYPE}" "${IMGDEPLOYDIR}/${IMAGE_NAME}.dataimg"
}
IMAGE_CMD_dataimg_mender-image-ubi() {
    mkfs.ubifs -o "${WORKDIR}/data.ubifs" -r "${IMAGE_ROOTFS}/data" ${MKUBIFS_ARGS}
    install -m 0644 "${WORKDIR}/data.ubifs" "${IMGDEPLOYDIR}/${IMAGE_NAME}.dataimg"
}

# We need the data contents intact.
do_image_dataimg[respect_exclude_path] = "0"

do_image_dataimg[depends] += "${@bb.utils.contains('DISTRO_FEATURES', 'mender-image-ubi', 'mtd-utils-native:do_populate_sysroot', '', d)}"
