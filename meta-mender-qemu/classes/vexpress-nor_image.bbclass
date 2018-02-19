inherit image_types

NORIMG = "${IMGDEPLOYDIR}/${IMAGE_NAME}${IMAGE_NAME_SUFFIX}.vexpress-nor"

# we need ubimg to be present
IMAGE_TYPEDEP_vexpress-nor = "ubimg"

IMAGE_CMD_vexpress-nor() {

    # MTD partitioning has the following layout:
    # 1m(u-boot)ro,
    # 1m(u-boot-env)ro,
    # -(ubi)

    # create a single NOR file image, fill with 0xff (empty) pattern
    dd if=/dev/zero bs=1M count=128 | tr '\000' '\377' > ${WORKDIR}/nor-full

    ubimgfile=${IMGDEPLOYDIR}/${IMAGE_BASENAME}-${MACHINE}.ubimg

    # ubi image starts at 2MB offset and must be smaller than 126MB
    imgsize=$(stat -c '%s' -L ${ubimgfile})
    if [ "$imgsize" -gt 132120576 ]; then
        bbfatal "image too large"
        exit 1
    fi

    dd if=${ubimgfile} of=${WORKDIR}/nor-full bs=1M seek=2 conv=notrunc

    # split into 2 * 64MB files, output files are named nor0 & nor1
    split -b 67108864 -a 1 -d ${WORKDIR}/nor-full ${WORKDIR}/nor

    tar -C ${WORKDIR} -c nor0 nor1 > ${NORIMG}
}
