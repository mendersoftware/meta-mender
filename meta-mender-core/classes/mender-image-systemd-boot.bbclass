# mender-image-systemd-boot: prepare image for a systemd-boot system

require conf/image-uefi.conf

do_uefiapp[vardeps] += "APPEND MENDER_ROOTFS_PART_A MENDER_ROOTFS_PART_B"
do_uefiapp[depends] += "systemd-mender-config-native:do_populate_sysroot"
inherit uefi-comboapp

# overridden from meta-intel
python create_uefiapps() {
    # We must clean up anything that matches the expected output pattern, to ensure that
    # the next steps do not accidentally use old files.
    import glob
    path = d.expand('${DEPLOY_DIR_IMAGE}/${IMAGE_LINK_NAME}')
    for old_efi in glob.glob(path + '.boot*.efi'):
        os.unlink(old_efi)

    append = d.getVar('APPEND')

    # Use A/B kernel suffixes with modified root= arguments
    d.setVar('APPEND', '%s root=%s' % (append, d.getVar('MENDER_ROOTFS_PART_A')))
    create_uefiapp(d, uuid=None, app_suffix='_a')
    d.setVar('APPEND', '%s root=%s' % (append, d.getVar('MENDER_ROOTFS_PART_B')))
    create_uefiapp(d, uuid=None, app_suffix='_b')

    from subprocess import check_call
    check_call("ab_setup.py init " + path + '.esp', shell=True)
}


# Copy unified kernel images images to /bin, so fw_setenv can pick them up when an upgrade
# is requested.
fakeroot do_uefiapp_deploy() {
    rm -rf ${IMAGE_ROOTFS}/boot/*
    dest=${IMAGE_ROOTFS}/bin
    mkdir -p $dest
    uefiapp_deploy_at $dest
}
