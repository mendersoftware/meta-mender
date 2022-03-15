rpi_install_firmware_to_rootfs() {
    install -d ${IMAGE_ROOTFS}/boot/firmware/overlays

    cp ${DEPLOY_DIR_IMAGE}/${BOOTFILES_DIR_NAME}/* ${IMAGE_ROOTFS}/boot/firmware/

    # To exclude files such as bcm2710-rpi-3-b-1-4.19.88+git0+988cc7beac-r0-raspberrypi3-20200323173633.dtb
    # as only the link names are actually valid and searched for on the device.
    find ${DEPLOY_DIR_IMAGE}/ -type l \( -iname "*.dtb" \) -exec cp {} ${IMAGE_ROOTFS}/boot/firmware/ \;
    find ${DEPLOY_DIR_IMAGE}/ -type l \( -iname "*.dtbo" \) -exec cp {} ${IMAGE_ROOTFS}/boot/firmware/overlays/ \;

    cp ${DEPLOY_DIR_IMAGE}/u-boot.bin ${IMAGE_ROOTFS}/boot/firmware/${SDIMG_KERNELIMAGE}
    cp ${DEPLOY_DIR_IMAGE}/boot.scr ${IMAGE_ROOTFS}/boot/firmware/
}
ROOTFS_POSTPROCESS_COMMAND += "rpi_install_firmware_to_rootfs; "

IMAGE_INSTALL:append = " update-firmware-state-script"
