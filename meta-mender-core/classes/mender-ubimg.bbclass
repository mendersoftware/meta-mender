# Class that creates an UBI image with an Mender layout

# The UBI volume scheme is:
#    ubi0: first rootfs, active
#    ubi1: second rootfs, inactive, mirror of first,
#           available as failsafe for when some update fails
#    ubi2: persistent data partition


inherit image
inherit image_types

do_image_ubimg[depends] += "mtd-utils-native:do_populate_sysroot rsync-native:do_populate_sysroot"

IMAGE_CMD_ubimg () {
    set -e -x

    # For some reason, logging is not working correctly inside IMAGE_CMD bodies,
    # so wrap all logging in these functions that also have an echo. This won't
    # prevent warnings from being hidden deep in log files, but there is nothing
    # we can do about that.
    ubimg_warning() {
        echo "$@"
        bbwarn "$@"
    }
    ubimg_fatal() {
        echo "$@"
        bbfatal "$@"
    }

    mkdir -p "${WORKDIR}"

    # Workaround for the fact that the image builder requires this directory,
    # despite not using it. If "rm_work" is enabled, this directory won't always
    # exist.
    mkdir -p "${IMAGE_ROOTFS}"

    if [ "${MENDER_BOOT_PART_SIZE_MB}" != "0" ]; then
        ubimg_fatal "Boot partition is not supported for ubimg. MENDER_BOOT_PART_SIZE_MB should be set to 0."
    fi

    if ${@bb.utils.contains("DISTRO_FEATURES", "mender-uboot", "true", "false", d)}; then
        # U-Boot doesn't allow putting both of the redundant environments on the
        # same volume, so we must split it and put each half on a separate volume.
        local uboot_env_vol_size=$(expr $(stat -c %s ${DEPLOY_DIR_IMAGE}/uboot.env) / 2)
        # Make sure it is divisible by the erase block.
        local alignment=${MENDER_PARTITION_ALIGNMENT}
        if [ $(expr $uboot_env_vol_size % $alignment || true) -ne 0 ]; then
            bbfatal "U-Boot environment size is not an even multiple of MENDER_PARTITION_ALIGNMENT ($alignment)."
        fi

        dd if=${DEPLOY_DIR_IMAGE}/uboot.env of=${WORKDIR}/ubimg-uboot-env-1 bs=$uboot_env_vol_size count=1
        dd if=${DEPLOY_DIR_IMAGE}/uboot.env of=${WORKDIR}/ubimg-uboot-env-2 bs=$uboot_env_vol_size skip=1 count=1
    fi

    cat > ${WORKDIR}/ubimg-${IMAGE_NAME}.cfg <<EOF
[rootfsA]
mode=ubi
image=${IMGDEPLOYDIR}/${IMAGE_LINK_NAME}.ubifs
vol_id=0
vol_size=${MENDER_CALC_ROOTFS_SIZE}KiB
vol_type=dynamic
vol_name=rootfsa

[rootfsB]
mode=ubi
image=${IMGDEPLOYDIR}/${IMAGE_LINK_NAME}.ubifs
vol_id=1
vol_size=${MENDER_CALC_ROOTFS_SIZE}KiB
vol_type=dynamic
vol_name=rootfsb

[data]
mode=ubi
image=${IMGDEPLOYDIR}/${IMAGE_LINK_NAME}.dataimg
vol_id=2
vol_size=${MENDER_DATA_PART_SIZE_MB}MiB
vol_type=dynamic
vol_name=data

EOF

    if ${@bb.utils.contains("DISTRO_FEATURES", "mender-uboot", "true", "false", d)}; then
        cat >> ${WORKDIR}/ubimg-${IMAGE_NAME}.cfg <<EOF
[u-boot-env-1]
mode=ubi
image=${WORKDIR}/ubimg-uboot-env-1
vol_id=${MENDER_UBOOT_ENV_UBIVOL_NUMBER_1}
vol_size=$uboot_env_vol_size
vol_type=dynamic
vol_name=u-boot-env-1

[u-boot-env-2]
mode=ubi
image=${WORKDIR}/ubimg-uboot-env-2
vol_id=${MENDER_UBOOT_ENV_UBIVOL_NUMBER_2}
vol_size=$uboot_env_vol_size
vol_type=dynamic
vol_name=u-boot-env-2

EOF
    fi

    cat ${WORKDIR}/ubimg-${IMAGE_NAME}.cfg

    ubinize -o ${IMGDEPLOYDIR}/${IMAGE_NAME}${IMAGE_NAME_SUFFIX}.ubimg ${UBINIZE_ARGS} ${WORKDIR}/ubimg-${IMAGE_NAME}.cfg

    # Cleanup cfg file
    mv ${WORKDIR}/ubimg-${IMAGE_NAME}.cfg ${IMGDEPLOYDIR}/

}

IMAGE_TYPEDEP_ubimg_append = " ubifs dataimg"

# So that we can use the files from excluded paths in the full images.
do_image_ubimg[respect_exclude_path] = "0"
