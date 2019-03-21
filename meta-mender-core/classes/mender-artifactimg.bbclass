inherit mender-helpers

# ------------------------------ CONFIGURATION ---------------------------------

# Extra arguments that should be passed to mender-artifact.
MENDER_ARTIFACT_EXTRA_ARGS ?= ""

# The key used to sign the mender update.
MENDER_ARTIFACT_SIGNING_KEY ?= ""

# --------------------------- END OF CONFIGURATION -----------------------------

do_image_mender[depends] += "mender-artifact-native:do_populate_sysroot"

ARTIFACTIMG_FSTYPE ??= "${ARTIFACTIMG_FSTYPE_DEFAULT}"
ARTIFACTIMG_FSTYPE_DEFAULT = "ext4"

ARTIFACTIMG_NAME ??= "${ARTIFACTIMG_NAME_DEFAULT}"
ARTIFACTIMG_NAME_DEFAULT = "${IMAGE_LINK_NAME}"

IMAGE_CMD_mender () {
    set -x

    if [ -z "${MENDER_ARTIFACT_NAME}" ]; then
        bbfatal "Need to define MENDER_ARTIFACT_NAME variable."
    fi

    rootfs_size=$(stat -Lc %s ${IMGDEPLOYDIR}/${ARTIFACTIMG_NAME}.${ARTIFACTIMG_FSTYPE})
    calc_rootfs_size=$(expr ${MENDER_CALC_ROOTFS_SIZE} \* 1024)
    if [ $rootfs_size -gt $calc_rootfs_size ]; then
        bbfatal "Size of rootfs is greater than the calculated partition space ($rootfs_size > $calc_rootfs_size). This image won't fit on a device with the current storage configuration. Try reducing IMAGE_OVERHEAD_FACTOR if it is higher than 1.0, or raise MENDER_STORAGE_TOTAL_SIZE_MB if the device in fact has more storage."
    fi

    if [ -z "${MENDER_DEVICE_TYPES_COMPATIBLE}" ]; then
        bbfatal "MENDER_DEVICE_TYPES_COMPATIBLE variable cannot be empty."
    fi

    extra_args=

    for dev in ${MENDER_DEVICE_TYPES_COMPATIBLE}; do
        extra_args="$extra_args -t $dev"
    done

    if [ -n "${MENDER_ARTIFACT_SIGNING_KEY}" ]; then
        extra_args="$extra_args -k ${MENDER_ARTIFACT_SIGNING_KEY}"
    fi

    if [ -d "${DEPLOY_DIR_IMAGE}/mender-state-scripts" ]; then
        extra_args="$extra_args -s ${DEPLOY_DIR_IMAGE}/mender-state-scripts"
    fi

    image_flag=-u
    if ${@mender_version_is_minimum(d, "mender-artifact", "3.0.0", "true", "false")}; then
        # There is no version 4.0.0 at this time. This was introduced as a way
        # to keep master building while 3.0.0 is still on a branch. Revert the
        # commit that introduced this as soon as 3.0.0 goes back to the master
        # branch.
        if ! ${@mender_version_is_minimum(d, "mender-artifact", "4.0.0", "true", "false")}; then
            image_flag=-f
        fi
    fi

    mender-artifact write rootfs-image \
        -n ${MENDER_ARTIFACT_NAME} \
        $extra_args \
        $image_flag ${IMGDEPLOYDIR}/${ARTIFACTIMG_NAME}.${ARTIFACTIMG_FSTYPE} \
        ${MENDER_ARTIFACT_EXTRA_ARGS} \
        -o ${IMGDEPLOYDIR}/${IMAGE_NAME}${IMAGE_NAME_SUFFIX}.mender
}

IMAGE_CMD_mender[vardepsexclude] += "IMAGE_ID"
# We need to have the filesystem image generated already.
IMAGE_TYPEDEP_mender_append = " ${ARTIFACTIMG_FSTYPE}"
