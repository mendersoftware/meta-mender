# Class to create the "bootimg" type, which contains the boot partition as a raw
# filesystem.

inherit mender-helpers

IMAGE_CMD_bootimg() {
    if [ ${MENDER_BOOT_PART_SIZE_MB} -ne 0 ]; then
        mender_merge_bootfs_and_image_boot_files
        rm -f "${WORKDIR}/boot.vfat"
        dd if=/dev/zero of="${WORKDIR}/boot.vfat" count=0 bs=1M seek=${MENDER_BOOT_PART_SIZE_MB}
        mkfs.vfat -n "BOOT" "${WORKDIR}/boot.vfat"
        for i in $(find ${WORKDIR}/bootfs.${BB_CURRENTTASK}/ -mindepth 1 -maxdepth 1); do
           mcopy -i "${WORKDIR}/boot.vfat" -s "$i" ::/
        done
        install -m 0644 "${WORKDIR}/boot.vfat" "${IMGDEPLOYDIR}/${IMAGE_NAME}.bootimg"
    fi
}

# We need the boot contents intact.
do_image_bootimg[respect_exclude_path] = "0"

do_image_bootimg[depends] += " \
    dosfstools-native:do_populate_sysroot \
    mtools-native:do_populate_sysroot \
"
