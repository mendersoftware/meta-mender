require u-boot-mender-common.inc

inherit deploy

do_provide_mender_defines_append() {
    # Since the auto-provided fw-utils recipe will typically not have access to
    # the proper BOOTENV_SIZE, let's create the fw_env.config file here, so that
    # the mender_tar_src stage will provide it in its tar file.

    if [ ! -e "${WORKDIR}/fw_env.config.default" ] && [ "${PREFERRED_PROVIDER_u-boot-fw-utils}" = "u-boot-fw-utils-mender-auto-provided" ]; then
        mender_create_fw_env_config_file ${WORKDIR}/fw_env.config.default
    fi
}

do_mender_tar_src() {
    cd ${WORKDIR}
    # Zip up all plain files, plus the git directory, but not the rest, because
    # there are a lot of bitbake data directories.
    tar czf ${TMPDIR}/mender-u-boot-src.tar.gz `find -maxdepth 1 -type f` git
}
python() {
    if bb.utils.contains('MENDER_UBOOT_AUTO_CONFIGURE', '1', True, False, d):
        aftertask = "do_mender_uboot_auto_configure"
    else:
        aftertask = "do_provide_mender_defines"
    bb.build.addtask('do_mender_tar_src', 'do_configure', aftertask, d)
}

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
