
IMAGE_DEPENDS_artifactimg = "artifacts-native"

ARTIFACTIMG_FSTYPE  ?= "ext4"
IMAGE_CMD_artifactimg = "artifacts write rootfs-image \
                      -i ${IMAGE_ID} -t ${DEVICE_TYPE}\
                      -u ${DEPLOY_DIR_IMAGE}/${IMAGE_BASENAME}-${MACHINE}.${ARTIFACTIMG_FSTYPE} \
                      -o ${DEPLOY_DIR_IMAGE}/${IMAGE_NAME}${IMAGE_NAME_SUFFIX}.artifactimg \
                      "

IMAGE_CMD_artifactimg[vardepsexclude] += "IMAGE_ID"

python() {
    fslist = d.getVar('IMAGE_FSTYPES', None).split()
    for fs in fslist:
        if fs in ["ext2", "ext3", "ext4"]:
            # We need to have the filesystem image generated already. Make it
            # dependent on all image types we support.
            d.setVar('IMAGE_TYPEDEP_artifactimg_append', " " + fs)
            d.setVar('ARTIFACTIMG_FSTYPE', fs)
}
