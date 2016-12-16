
IMAGE_DEPENDS_mender = "mender-artifact-native"

ARTIFACTIMG_FSTYPE  ?= "ext4"
IMAGE_CMD_mender () {
    set -x

    if [ -z "${MENDER_ARTIFACT_NAME}" ]; then
        bberror "Need to define MENDER_ARTIFACT_NAME variable."
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
