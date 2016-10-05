
IMAGE_DEPENDS_mender = "artifacts-native"

ARTIFACTIMG_FSTYPE  ?= "ext4"
IMAGE_CMD_mender = "artifacts write rootfs-image \
                      -i ${IMAGE_ID} -t ${DEVICE_TYPE}\
                      -u ${IMGDEPLOYDIR}/${IMAGE_BASENAME}-${MACHINE}.${ARTIFACTIMG_FSTYPE} \
                      -o ${IMGDEPLOYDIR}/${IMAGE_NAME}${IMAGE_NAME_SUFFIX}.mender \
                      "

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
