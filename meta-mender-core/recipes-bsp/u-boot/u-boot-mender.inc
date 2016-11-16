# This file used to be included by both u-boot and u-boot-fw-utils, but not
# anymore. Do this check in order to help those who already are using it in
# their build. This can probably be removed after enough time has passed.
python() {
    in_pn = (d.getVar('PN', True) == 'u-boot-fw-utils')
    in_provides = ('u-boot-fw-utils' in d.getVar('PROVIDES', True).split())
    in_rprovides = ('u-boot-fw-utils' in d.getVar('RPROVIDES', True).split())
    if in_pn or in_provides or in_rprovides:
        bb.fatal("u-boot-mender.inc should not be included from a u-boot-fw-utils recipe anymore. Include u-boot-fw-utils-mender.inc instead!")
}

require u-boot-mender-common.inc

# Copy script to the deploy area with u-boot, uImage, and rootfs
do_deploy_uenv () {
    if [ -e ${WORKDIR}/uEnv.txt ] ; then
        install -d ${DEPLOY_DIR_IMAGE}
        install -m 0444 ${WORKDIR}/uEnv.txt ${DEPLOY_DIR_IMAGE}
    fi
}
addtask deploy_uenv before do_package after do_install
