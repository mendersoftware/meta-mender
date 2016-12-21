require u-boot-mender-common.inc

inherit deploy

do_deploy_append() {
    # Copy script to the deploy area with u-boot, uImage, and rootfs
    if [ -e ${WORKDIR}/uEnv.txt ] ; then
        install -d ${DEPLOYDIR}
        install -m 0444 ${WORKDIR}/uEnv.txt ${DEPLOYDIR}
    fi

    # Creates the blob that will be the U-Boot environment, with proper
    # alignment. This will be used later by the image creation recipe. The file
    # is filled with null right now, although it could be filled with the actual
    # environment. For now we're primarily interested in the size.
    # Note: We cannot use a sparse file here, even though it's filled with
    # zeros, because the build process uses "du" to determine the size of this
    # file.
    MENDER_BOOTENV_TOTAL_ALIGNED_SIZE_SECTORS=$(expr ${MENDER_BOOTENV_TOTAL_ALIGNED_SIZE} / 512)
    dd if=/dev/zero of=${WORKDIR}/uboot.env count=$MENDER_BOOTENV_TOTAL_ALIGNED_SIZE_SECTORS
    install -m 644 ${WORKDIR}/uboot.env ${DEPLOYDIR}/uboot.env
}
addtask deploy after do_compile
