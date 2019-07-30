inherit image_types

# we need ubimg to be present
IMAGE_TYPEDEP_vexpress-nor = "mtdimg"

IMAGE_CMD_vexpress-nor() {
    set -ex

    mtdimgfile=${IMGDEPLOYDIR}/${IMAGE_LINK_NAME}.mtdimg

    imgsize=$(stat -c '%s' -L ${mtdimgfile})
    if [ "$imgsize" -gt 134217728 ]; then
        bbfatal "Image too large for QEMU vexpress-nor image (max 128MiB)"
        exit 1
    fi

    dd if=/dev/zero of=${WORKDIR}/vexpress-nor bs=1M count=128
    dd if=${mtdimgfile} of=${WORKDIR}/vexpress-nor conv=notrunc

    # split into 2 * 64MB files, output files are named nor0 & nor1
    split -b 67108864 -a 1 -d ${WORKDIR}/vexpress-nor ${WORKDIR}/nor

    tar -C ${WORKDIR} -c nor0 nor1 > ${IMGDEPLOYDIR}/${IMAGE_NAME}${IMAGE_NAME_SUFFIX}.vexpress-nor
}
