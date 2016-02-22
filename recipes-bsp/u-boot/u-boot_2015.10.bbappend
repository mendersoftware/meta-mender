# Keep this separately from the rest of the .bb file in case that .bb file is
# overridden from another layer.

FILESEXTRAPATHS_prepend := "${THISDIR}/files:"

SRC_URI_append_beaglebone = "file://0001-beaglebone-mender-specific-configuration.patch \
                            file://uEnv.txt"

# Copy script to the deploy area with u-boot, uImage, and rootfs
do_deploy_uenv () {
    if [ -e ${WORKDIR}/uEnv.txt ] ; then
        install -d ${DEPLOY_DIR_IMAGE}
        install -m 0444 ${WORKDIR}/uEnv.txt ${DEPLOY_DIR_IMAGE}
    fi
}
addtask deploy_uenv before do_package after do_install

