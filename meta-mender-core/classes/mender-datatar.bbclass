# Class to create the "datatar" type, which contains the data partition as a raw
# filesystem.

inherit mender-bootstrap-artifact

IMAGE_CMD_datatar() {
    tar -cf "${WORKDIR}/data.tar" -C "${_MENDER_ROOTFS_COPY}" .
    install -m 0644 "${WORKDIR}/data.tar" "${IMGDEPLOYDIR}/${IMAGE_NAME}.data.tar"
    ln -sfn "${IMAGE_NAME}.data.tar" "${IMGDEPLOYDIR}/${IMAGE_LINK_NAME}.data.tar"
}

# We need the data contents intact.
do_image_datatar[respect_exclude_path] = "0"

do_image_datatar[prefuncs] += " do_copy_rootfs do_install_bootstrap_artifact"
do_image_datatar[postfuncs] += " do_delete_copy_rootfs"

IMAGE_TYPEDEP_datatar_append = " bootstrap-artifact"
