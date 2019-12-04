# Class to create the "datatar" type, which contains the data partition as a raw
# filesystem.

IMAGE_CMD_datatar() {
    tar -cf "${WORKDIR}/data.tar" -C "${IMAGE_ROOTFS}/data" .
    install -m 0644 "${WORKDIR}/data.tar" "${IMGDEPLOYDIR}/${IMAGE_NAME}.data.tar"
    ln -sfn "${IMAGE_NAME}.data.tar" "${IMGDEPLOYDIR}/${IMAGE_LINK_NAME}.data.tar"
}

# We need the data contents intact.
do_image_datatar[respect_exclude_path] = "0"
