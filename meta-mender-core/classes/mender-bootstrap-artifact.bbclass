IMAGE_CMD_bootstrap-artifact() {

    if [ -z "${MENDER_ARTIFACT_NAME}" ]; then
            bberror "Need to define MENDER_ARTIFACT_NAME variable."
            exit 1
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

        if [ -n "${MENDER_ARTIFACT_NAME_DEPENDS}" ]; then
            cmd=""
            apply_arguments "--artifact-name-depends" "${MENDER_ARTIFACT_NAME_DEPENDS}"
            extra_args="$extra_args  $cmd"
        fi

        if [ -n "${MENDER_ARTIFACT_PROVIDES}" ]; then
            cmd=""
            apply_arguments "--provides" "${MENDER_ARTIFACT_PROVIDES}"
            extra_args="$extra_args  $cmd"
        fi

        if [ -n "${MENDER_ARTIFACT_PROVIDES_GROUP}" ]; then
            cmd=""
            apply_arguments "--provides-group" "${MENDER_ARTIFACT_PROVIDES_GROUP}"
            extra_args="$extra_args $cmd"
        fi

        if [ -n "${MENDER_ARTIFACT_DEPENDS}" ]; then
            cmd=""
            apply_arguments "--depends" "${MENDER_ARTIFACT_DEPENDS}"
            extra_args="$extra_args $cmd"
        fi

        if [ -n "${MENDER_ARTIFACT_DEPENDS_GROUPS}" ]; then
            cmd=""
            apply_arguments "--depends-groups" "${MENDER_ARTIFACT_DEPENDS_GROUPS}"
            extra_args="$extra_args $cmd"
        fi

        img_checksum="$(sha256sum --binary ${IMGDEPLOYDIR}/${IMAGE_LINK_NAME}.${ARTIFACTIMG_FSTYPE} | cut --delimiter=' ' --fields=1)"

        if [ -z "${img_checksum}" ]; then
            bberror "The image checksum cannot be empty"
        fi

        # NOTE: We don't allow extra arguments from MENDER_ARTIFACT_EXTRA_ARGS
        mender-artifact write bootstrap-artifact \
            --artifact-name ${MENDER_ARTIFACT_NAME} \
            --provides "rootfs-image.version:${MENDER_ARTIFACT_NAME}" \
            --provides "rootfs-image.checksum:${img_checksum}" \
            --clears-provides "rootfs-image.*" \
            $extra_args \
            --output-path "${IMGDEPLOYDIR}/${IMAGE_NAME}${IMAGE_SUFFIX}.bootstrap-artifact" \
            --version 3 # Always write version 3

}

do_image_bootstrap_artifact[respect_exclude_path] = "0"
do_image_bootstrap_artifact[depends] += " mender-artifact-native:do_populate_sysroot"
IMAGE_TYPEDEP_bootstrap-artifact_append = " ${ARTIFACTIMG_FSTYPE}"

python do_copy_rootfs() {
    from oe.path import copyhardlinktree

    _from = os.path.realpath(os.path.join(d.getVar("IMAGE_ROOTFS"), "data"))
    _to = os.path.realpath(os.path.join(d.getVar("WORKDIR"), "data.copy.%s" % d.getVar('BB_CURRENTTASK')))

    copyhardlinktree(_from, _to)

    d.setVar('_MENDER_ROOTFS_COPY', _to)
}

python do_delete_copy_rootfs() {
    import subprocess

    copy_dir = d.getVar('_MENDER_ROOTFS_COPY')

    subprocess.check_call(["rm", "-rf", copy_dir])
}

fakeroot do_install_bootstrap_artifact () {
    install -m 0400 "${IMGDEPLOYDIR}/${IMAGE_LINK_NAME}.bootstrap-artifact" "${_MENDER_ROOTFS_COPY}/mender/bootstrap.mender"
}
