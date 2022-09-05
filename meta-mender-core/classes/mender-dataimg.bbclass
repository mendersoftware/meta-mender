# Class to create the "dataimg" type, which contains the data partition as a raw
# filesystem.

IMAGE_CMD_dataimg() {
    if [ ${MENDER_DATA_PART_FSTYPE_TO_GEN} = "btrfs" ]; then
        force_flag="-f"
        root_dir_flag="-r ${IMAGE_ROOTFS}/data"
        volume_label_flag="-L"
    elif [ ${MENDER_DATA_PART_FSTYPE_TO_GEN} = "f2fs" ]; then
        force_flag="-f"
        root_dir_flag=""
        volume_label_flag="-l"
    else #Assume ext3/4
        force_flag="-F"
        root_dir_flag="-d ${IMAGE_ROOTFS}/data"
        volume_label_flag="-L"
    fi

    dd if=/dev/zero of="${WORKDIR}/data.${MENDER_DATA_PART_FSTYPE_TO_GEN}" count=0 bs=1M seek=${MENDER_DATA_PART_SIZE_MB}
    mkfs.${MENDER_DATA_PART_FSTYPE_TO_GEN} \
        $force_flag \
        "${WORKDIR}/data.${MENDER_DATA_PART_FSTYPE_TO_GEN}" \
        $root_dir_flag \
        $volume_label_flag "${MENDER_DATA_PART_LABEL}" \
        ${MENDER_DATA_PART_FSOPTS}

    if [ ${MENDER_DATA_PART_FSTYPE_TO_GEN} = "f2fs" ]; then
        sload.f2fs -f "${IMAGE_ROOTFS}/data" "${WORKDIR}/data.${MENDER_DATA_PART_FSTYPE_TO_GEN}"
    fi

    install -m 0644 "${WORKDIR}/data.${MENDER_DATA_PART_FSTYPE_TO_GEN}" "${IMGDEPLOYDIR}/${IMAGE_NAME}.dataimg"
}
IMAGE_CMD_dataimg_mender-image-ubi() {
    mkfs.ubifs -o "${WORKDIR}/data.ubifs" -r "${IMAGE_ROOTFS}/data" ${MKUBIFS_ARGS}
    install -m 0644 "${WORKDIR}/data.ubifs" "${IMGDEPLOYDIR}/${IMAGE_NAME}.dataimg"
}

shasum_rootfs_img() {
    bbwarn "Shasumming the ext4 image..."
    sha256sum --binary ${IMGDEPLOYDIR}/${IMAGE_NAME}${IMAGE_NAME_SUFFIX}.${ARTIFACTIMG_FSTYPE} > "${IMGDEPLOYDIR}/${IMAGE_LINK_NAME}.checksum"
}

do_generate_bootstrap_artifact() {

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

        img_checksum="$(cat ${IMGDEPLOYDIR}/${IMAGE_LINK_NAME}.checksum | cut --delimiter=' ' --fields=1)"

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
            --output-path "${WORKDIR}/bootstrap.mender" \
            --version 3 # Always write version 3

}

do_install_bootstrap_artifact[respect_exclude_path] = "0"

fakeroot do_install_bootstrap_artifact () {
    bbwarn "Installing the bootstrap Artifact into /data/mender..."
    install -m 0400 "${WORKDIR}/bootstrap.mender" "${IMAGE_ROOTFS}/data/mender/bootstrap.mender"
    bbwarn "Installed the bootstrap Artifact into /data/mender..."
}

# We need the data contents intact.
do_image_dataimg[respect_exclude_path] = "0"

do_image_dataimg[depends] += "${@bb.utils.contains('MENDER_FEATURES', 'mender-image-ubi', 'mtd-utils-native:do_populate_sysroot', '', d)}"
do_image_dataimg[depends] += "${@bb.utils.contains('MENDER_DATA_PART_FSTYPE_TO_GEN', 'btrfs','btrfs-tools-native:do_populate_sysroot','',d)}"
do_image_dataimg[depends] += "${@bb.utils.contains_any('MENDER_DATA_PART_FSTYPE_TO_GEN', 'ext2 ext3 ext4','e2fsprogs-native:do_populate_sysroot','',d)}"
do_image_dataimg[depends] += "${@bb.utils.contains('MENDER_DATA_PART_FSTYPE_TO_GEN', 'f2fs','f2fs-tools-native:do_populate_sysroot','',d)}"
do_image_dataimg[depends] += " mender-artifact-native:do_populate_sysroot"

do_image_dataimg[prefuncs] += " do_generate_bootstrap_artifact do_install_bootstrap_artifact"

IMAGE_TYPEDEP_dataimg_append = " ${ARTIFACTIMG_FSTYPE}"

python() {
    image_type = d.getVar("ARTIFACTIMG_FSTYPE")
    if image_type == "":
        bb.fatal("No 'ARTIFACTIMG_FSTYPE' set")

    image_job = "do_image_{}".format(image_type)

    d.appendVarFlag(image_job, "postfuncs", " shasum_rootfs_img ")
}

