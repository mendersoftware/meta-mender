# Class to create the "dataimg" type, which contains the data partition as a raw
# filesystem.

inherit mender-bootstrap-artifact

IMAGE_CMD_dataimg() {
    if [ ${MENDER_DATA_PART_FSTYPE_TO_GEN} = "btrfs" ]; then
        force_flag="-f"
        root_dir_flag="-r ${_MENDER_ROOTFS_COPY}"
        volume_label_flag="-L"
    elif [ ${MENDER_DATA_PART_FSTYPE_TO_GEN} = "f2fs" ]; then
        force_flag="-f"
        root_dir_flag=""
        volume_label_flag="-l"
    else #Assume ext3/4
        force_flag="-F"
        root_dir_flag="-d ${_MENDER_ROOTFS_COPY}"
        volume_label_flag="-L"
    fi

    dd if=/dev/zero of="${WORKDIR}/data.${MENDER_DATA_PART_FSTYPE_TO_GEN}" count=0 bs=1M seek=${MENDER_DATA_PART_SIZE_MB}
    mkfs.${MENDER_DATA_PART_FSTYPE_TO_GEN} \
        $force_flag \
        "${WORKDIR}/data.${MENDER_DATA_PART_FSTYPE_TO_GEN}" \
        $root_dir_flag \
        $volume_label_flag "${MENDER_DATA_PART_LABEL}" \
        ${MENDER_DATA_PART_FSOPTS}

    if [ ${MENDER_DATA_PART_FSTYPE_TO_GEN} = "f2fs" ]; then
        sload.f2fs -f "${_MENDER_ROOTFS_COPY}" "${WORKDIR}/data.${MENDER_DATA_PART_FSTYPE_TO_GEN}"
    fi

    install -m 0644 "${WORKDIR}/data.${MENDER_DATA_PART_FSTYPE_TO_GEN}" "${IMGDEPLOYDIR}/${IMAGE_NAME}.dataimg"
}
IMAGE_CMD_dataimg_mender-image-ubi() {
    mkfs.ubifs -o "${WORKDIR}/data.ubifs" -r "${_MENDER_ROOTFS_COPY}" ${MKUBIFS_ARGS}
    install -m 0644 "${WORKDIR}/data.ubifs" "${IMGDEPLOYDIR}/${IMAGE_NAME}.dataimg"
}

# We need the data contents intact.
do_image_dataimg[respect_exclude_path] = "0"

do_image_dataimg[depends] += "${@bb.utils.contains('MENDER_FEATURES', 'mender-image-ubi', 'mtd-utils-native:do_populate_sysroot', '', d)}"
do_image_dataimg[depends] += "${@bb.utils.contains('MENDER_DATA_PART_FSTYPE_TO_GEN', 'btrfs','btrfs-tools-native:do_populate_sysroot','',d)}"
do_image_dataimg[depends] += "${@bb.utils.contains_any('MENDER_DATA_PART_FSTYPE_TO_GEN', 'ext2 ext3 ext4','e2fsprogs-native:do_populate_sysroot','',d)}"
do_image_dataimg[depends] += "${@bb.utils.contains('MENDER_DATA_PART_FSTYPE_TO_GEN', 'f2fs','f2fs-tools-native:do_populate_sysroot','',d)}"

do_image_dataimg[prefuncs] += " do_copy_rootfs do_install_bootstrap_artifact"
do_image_dataimg[postfuncs] += " do_delete_copy_rootfs"

IMAGE_TYPEDEP_dataimg_append = " bootstrap-artifact"
