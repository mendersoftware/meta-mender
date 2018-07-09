# Class that creates an UBI image with an Mender layout

# The UBI volume scheme is:
#    ubi0: first rootfs, active
#    ubi1: second rootfs, inactive, mirror of first,
#           available as failsafe for when some update fails
#    ubi2: persistent data partition


########## CONFIGURATION START - you can override these default
##########                       values in your local.conf

IMAGE_TYPEDEP_ubimg_append = "ubifs"

########## CONFIGURATION END ##########

inherit image
inherit image_types

do_image_ubimg[depends] += "mtd-utils-native:do_populate_sysroot rsync-native:do_populate_sysroot"

IMAGE_CMD_ubimg () {
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

    echo \[rootfsA\] >> ${WORKDIR}/ubimg-${IMAGE_NAME}.cfg
    echo mode=ubi >> ${WORKDIR}/ubimg-${IMAGE_NAME}.cfg
    echo image=${IMGDEPLOYDIR}/${IMAGE_BASENAME}-${MACHINE}.ubifs >> ${WORKDIR}/ubimg-${IMAGE_NAME}.cfg
    echo vol_id=0 >> ${WORKDIR}/ubimg-${IMAGE_NAME}.cfg
    echo vol_size=${MENDER_CALC_ROOTFS_SIZE}KiB >> ${WORKDIR}/ubimg-${IMAGE_NAME}.cfg
    echo vol_type=dynamic >> ${WORKDIR}/ubimg-${IMAGE_NAME}.cfg
    echo vol_name=rootfsa >> ${WORKDIR}/ubimg-${IMAGE_NAME}.cfg
    echo "" >> ${WORKDIR}/ubimg-${IMAGE_NAME}.cfg

    echo \[rootfsB\] >> ${WORKDIR}/ubimg-${IMAGE_NAME}.cfg
    echo mode=ubi >> ${WORKDIR}/ubimg-${IMAGE_NAME}.cfg
    echo image=${IMGDEPLOYDIR}/${IMAGE_BASENAME}-${MACHINE}.ubifs >> ${WORKDIR}/ubimg-${IMAGE_NAME}.cfg
    echo vol_id=1 >> ${WORKDIR}/ubimg-${IMAGE_NAME}.cfg
    echo vol_size=${MENDER_CALC_ROOTFS_SIZE}KiB >> ${WORKDIR}/ubimg-${IMAGE_NAME}.cfg
    echo vol_type=dynamic >> ${WORKDIR}/ubimg-${IMAGE_NAME}.cfg
    echo vol_name=rootfsb >> ${WORKDIR}/ubimg-${IMAGE_NAME}.cfg
    echo "" >> ${WORKDIR}/ubimg-${IMAGE_NAME}.cfg

    echo \[data\] >> ${WORKDIR}/ubimg-${IMAGE_NAME}.cfg
    echo mode=ubi >> ${WORKDIR}/ubimg-${IMAGE_NAME}.cfg
    echo image=${IMGDEPLOYDIR}/data.ubifs >> ${WORKDIR}/ubimg-${IMAGE_NAME}.cfg
    echo vol_id=2 >> ${WORKDIR}/ubimg-${IMAGE_NAME}.cfg
    echo vol_size=${MENDER_DATA_PART_SIZE_MB}MiB >> ${WORKDIR}/ubimg-${IMAGE_NAME}.cfg
    echo vol_type=dynamic >> ${WORKDIR}/ubimg-${IMAGE_NAME}.cfg
    echo vol_name=data >> ${WORKDIR}/ubimg-${IMAGE_NAME}.cfg
    echo "" >> ${WORKDIR}/ubimg-${IMAGE_NAME}.cfg

    rm -rf "${WORKDIR}/data" || true
    mkdir -p "${WORKDIR}/data"

    if [ -n "${MENDER_DATA_PART_DIR}" ]; then
        rsync -a --no-owner --no-group ${MENDER_DATA_PART_DIR}/* "${WORKDIR}/data"
        chown -R root:root "${WORKDIR}/data"
    fi

    if [ -f "${DEPLOY_DIR_IMAGE}/data.tar" ]; then
        ( cd "${WORKDIR}" && tar xf "${DEPLOY_DIR_IMAGE}/data.tar" )
    fi

    mkdir -p "${WORKDIR}/data/mender"
    echo "device_type=${MENDER_DEVICE_TYPE}" > "${WORKDIR}/data/mender/device_type"
    chmod 0444 "${WORKDIR}/data/mender/device_type"

    # Create data UBIFS image
    mkfs.ubifs -o "${IMGDEPLOYDIR}/data.ubifs" -r "${WORKDIR}/data" ${MKUBIFS_ARGS}

    ubinize -o ${IMGDEPLOYDIR}/${IMAGE_NAME}${IMAGE_NAME_SUFFIX}.ubimg ${UBINIZE_ARGS} ${WORKDIR}/ubimg-${IMAGE_NAME}.cfg

    # Cleanup cfg file
    mv ${WORKDIR}/ubimg-${IMAGE_NAME}.cfg ${IMGDEPLOYDIR}/

}

IMAGE_TYPEDEP_ubimg_append = " ubifs"
