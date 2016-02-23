# Keep this separately from the rest of the .bb file in case that .bb file is
# overridden from another layer.

require u-boot-mender.inc

# Copy script to the deploy area with u-boot, uImage, and rootfs
do_deploy_uenv () {
    if [ -e ${WORKDIR}/uEnv.txt ] ; then
        install -d ${DEPLOY_DIR_IMAGE}
        install -m 0444 ${WORKDIR}/uEnv.txt ${DEPLOY_DIR_IMAGE}
    fi
}
addtask deploy_uenv before do_package after do_install

