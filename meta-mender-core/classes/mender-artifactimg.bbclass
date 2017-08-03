# Extra arguments that should be passed to mender-artifact.
MENDER_ARTIFACT_EXTRA_ARGS ?= ""

IMAGE_DEPENDS_mender = "mender-artifact-native"

ARTIFACTIMG_FSTYPE  ?= "ext4"
IMAGE_CMD_mender () {
    set -x

    if [ -z "${MENDER_ARTIFACT_NAME}" ]; then
        bbfatal "Need to define MENDER_ARTIFACT_NAME variable."
    fi

    rootfs_size=$(stat -Lc %s ${IMGDEPLOYDIR}/${IMAGE_BASENAME}-${MACHINE}.${ARTIFACTIMG_FSTYPE})
    calc_rootfs_size=$(expr ${MENDER_CALC_ROOTFS_SIZE} \* 1024)
    if [ $rootfs_size -gt $calc_rootfs_size ]; then
        bbfatal "Size of rootfs is greater than the calculated partition space ($rootfs_size > $calc_rootfs_size). This image won't fit on a device with the current storage configuration. Try reducing IMAGE_OVERHEAD_FACTOR if it is higher than 1.0, or raise MENDER_STORAGE_TOTAL_SIZE_MB if the device in fact has more storage."
    fi

    # Trim leading/trailing spaces, and replace spaces with commas for
    # consumption by mender-artifact tool.
    devs_compatible=
    sep=
    for dev in ${MENDER_DEVICE_TYPES_COMPATIBLE}; do
        devs_compatible="$devs_compatible$sep$dev"
        sep=,
    done

    if [ -z "$devs_compatible" ]; then
        bberror "MENDER_DEVICE_TYPES_COMPATIBLE variable cannot be empty."
    fi

    extra_args=

    if [ -d "${DEPLOY_DIR_IMAGE}/mender-state-scripts" ]; then
        extra_args="$extra_args -s ${DEPLOY_DIR_IMAGE}/mender-state-scripts"
    fi

    mender-artifact write rootfs-image \
        -n ${MENDER_ARTIFACT_NAME} -t "$devs_compatible" \
        $extra_args \
        -u ${IMGDEPLOYDIR}/${IMAGE_BASENAME}-${MACHINE}.${ARTIFACTIMG_FSTYPE} \
        ${MENDER_ARTIFACT_EXTRA_ARGS} \
        -o ${IMGDEPLOYDIR}/${IMAGE_NAME}${IMAGE_NAME_SUFFIX}.mender
}

IMAGE_CMD_mender[vardepsexclude] += "IMAGE_ID"

python() {
    fslist = d.getVar('IMAGE_FSTYPES', None).split()
    for fs in fslist:
        if fs in ["ext2", "ext3", "ext4"]:
            # We need to have the filesystem image generated already. Make it
            # dependent on all image types we support.
            d.setVar('IMAGE_TYPEDEP_mender_append', " " + fs)
            d.setVar('ARTIFACTIMG_FSTYPE', fs)
}
