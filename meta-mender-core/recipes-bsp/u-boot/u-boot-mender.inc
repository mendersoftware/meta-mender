require u-boot-mender-common.inc

# Copy script to the deploy area with u-boot, uImage, and rootfs
do_deploy_uenv () {
    if [ -e ${WORKDIR}/uEnv.txt ] ; then
        install -d ${DEPLOYDIR}
        install -m 0444 ${WORKDIR}/uEnv.txt ${DEPLOYDIR}
    fi
}
addtask deploy_uenv before do_package after do_install
