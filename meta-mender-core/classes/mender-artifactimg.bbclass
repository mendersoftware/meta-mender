# This is missing in krogoth, so define it ourselves in order to avoid having to
# change all the places that reference it.
IMGDEPLOYDIR = "${WORKDIR}/deploy-${PN}-image-complete"

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
        bbwarn "Size of rootfs is greater than the calculated partition space ($rootfs_size > $calc_rootfs_size). This image won't fit on a device with the current storage configuration. Make sure IMAGE_ROOTFS_EXTRA_SPACE is set to 0, and try reducing IMAGE_OVERHEAD_FACTOR if it is higher than 1.0."
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

    mender-artifact write rootfs-image \
        -n ${MENDER_ARTIFACT_NAME} -t "$devs_compatible" \
        -u ${IMGDEPLOYDIR}/${IMAGE_BASENAME}-${MACHINE}.${ARTIFACTIMG_FSTYPE} \
        -o ${IMGDEPLOYDIR}/${IMAGE_NAME}${IMAGE_NAME_SUFFIX}.mender \
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
