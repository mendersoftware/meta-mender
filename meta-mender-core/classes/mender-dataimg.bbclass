# Class to create the "dataimg" type, which contains the data partition as a raw
# filesystem.

IMAGE_CMD_dataimg() {
    if [ ${MENDER_DATA_PART_FSTYPE_TO_GEN} = "btrfs" ]; then
        force_flag="-f"
        root_dir_flag="-r"
    else #Assume ext3/4
        force_flag="-F"
        root_dir_flag="-d"
    fi

    dd if=/dev/zero of="${WORKDIR}/data.${MENDER_DATA_PART_FSTYPE_TO_GEN}" count=0 bs=1M seek=${MENDER_DATA_PART_SIZE_MB}
    mkfs.${MENDER_DATA_PART_FSTYPE_TO_GEN} \
        $force_flag \
        "${WORKDIR}/data.${MENDER_DATA_PART_FSTYPE_TO_GEN}" \
        $root_dir_flag "${IMAGE_ROOTFS}/data" \
        -L data \
        ${MENDER_DATA_PART_FSOPTS}
    install -m 0644 "${WORKDIR}/data.${MENDER_DATA_PART_FSTYPE_TO_GEN}" "${IMGDEPLOYDIR}/${IMAGE_NAME}.dataimg"
}
IMAGE_CMD_dataimg_mender-image-ubi() {
    mkfs.ubifs -o "${WORKDIR}/data.ubifs" -r "${IMAGE_ROOTFS}/data" ${MKUBIFS_ARGS}
    install -m 0644 "${WORKDIR}/data.ubifs" "${IMGDEPLOYDIR}/${IMAGE_NAME}.dataimg"
}

# We need the data contents intact.
do_image_dataimg[respect_exclude_path] = "0"

do_image_dataimg[depends] += "${@bb.utils.contains('DISTRO_FEATURES', 'mender-image-ubi', 'mtd-utils-native:do_populate_sysroot', '', d)}"
do_image_dataimg[depends] += "${@bb.utils.contains('MENDER_DATA_PART_FSTYPE_TO_GEN', 'btrfs','btrfs-tools-native:do_populate_sysroot','',d)}"
do_image_dataimg[depends] += "${@bb.utils.contains_any('MENDER_DATA_PART_FSTYPE_TO_GEN', 'ext2 ext3 ext4','e2fsprogs-native:do_populate_sysroot','',d)}"
