# Class to create the "bootimg" type, which contains the boot partition as a raw
# filesystem.

inherit mender-helpers

IMAGE_CMD_bootimg() {
    if [ ${MENDER_BOOT_PART_SIZE_MB} -ne 0 ]; then
        if [ ${MENDER_BOOT_PART_FSTYPE_TO_GEN} = "vfat" ]; then
            force_flag=""
            root_dir_flag=""
            label_flag="-n"
        elif [ ${MENDER_BOOT_PART_FSTYPE_TO_GEN} = "btrfs" ]; then
            force_flag="-f"
            root_dir_flag="-r"
            label_flag="-L"
        elif [ ${MENDER_BOOT_PART_FSTYPE_TO_GEN} = "ext4" ] || \
             [ ${MENDER_BOOT_PART_FSTYPE_TO_GEN} = "ext3" ] || \
             [ ${MENDER_BOOT_PART_FSTYPE_TO_GEN} = "ext2" ] ; then
            force_flag="-F"
            root_dir_flag="-d"
            label_flag="-L"
        else
            bbfatal "Unknown FSTYPE ${MENDER_BOOT_PART_FSTYPE_TO_GEN} for generating bootimg file."
        fi

        mender_merge_bootfs_and_image_boot_files
        rm -f "${WORKDIR}/boot.${MENDER_BOOT_PART_FSTYPE_TO_GEN}"
        dd if=/dev/zero of="${WORKDIR}/boot.${MENDER_BOOT_PART_FSTYPE_TO_GEN}" count=0 bs=1M seek=${MENDER_BOOT_PART_SIZE_MB}
        if [ ${MENDER_BOOT_PART_FSTYPE_TO_GEN} = "vfat" ]; then
            mkfs.${MENDER_BOOT_PART_FSTYPE_TO_GEN} \
                $force_flag \
                "${WORKDIR}/boot.${MENDER_BOOT_PART_FSTYPE_TO_GEN}" \
                ${MENDER_BOOT_PART_FSOPTS} $label_flag "BOOT"
            for i in $(find ${WORKDIR}/bootfs.${BB_CURRENTTASK}/ -mindepth 1 -maxdepth 1); do
               mcopy -i "${WORKDIR}/boot.vfat" -s "$i" ::/
            done
        else
            mkfs.${MENDER_BOOT_PART_FSTYPE_TO_GEN} \
                $force_flag \
                "${WORKDIR}/boot.${MENDER_BOOT_PART_FSTYPE_TO_GEN}" \
                $root_dir_flag "${WORKDIR}/bootfs.${BB_CURRENTTASK}" \
                $label_flag boot \
                ${MENDER_BOOT_PART_FSOPTS}
        fi
        install -m 0644 "${WORKDIR}/boot.${MENDER_BOOT_PART_FSTYPE_TO_GEN}" "${IMGDEPLOYDIR}/${IMAGE_NAME}.bootimg"
    fi
}

# We need the boot contents intact.
do_image_bootimg[respect_exclude_path] = "0"

do_image_bootimg[depends] += " \
    dosfstools-native:do_populate_sysroot \
    mtools-native:do_populate_sysroot \
"
