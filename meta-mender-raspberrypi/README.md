# meta-mender-raspberrypi

This Yocto layers contains recipes which enables support of building Mender client for Raspberry Pi boards.

**NOTE!**. To be able to support update of Linux kernel and DTB, Mender requires these to be installed in the `/boot` directory for each rootfs (normally /dev/mmcblk0p2 and /dev/mmcblk0p3). On the other hand, the Raspberry Pi boot firmware requires that the DTB file is in the same partition as the boot firmware (/dev/mmcbl0p1) and the config.txt file. For now Mender will not use the DTB that is delivered with new artifacts and will continue to boot with the original DTB that was populated using the SDIMG file.

Above should not pose any problems if you do not require any changes in `config.txt` and the default configuration certainly is enough to run Mender client.

## Dependencies

This layer depends on:

    URI: git://git.yoctoproject.org/meta-raspberrypi
    branch: master
    revision: HEAD

in addition to `meta-mender` dependencies.

## Build instructions

- Read [the Mender documentation on Building a Mender Yocto image](https://docs.mender.io/Artifacts/Building-Mender-Yocto-image) for Mender specific configuration.
- Set MACHINE to one of the following
    - raspberrypi
    - raspberrypi0
    - raspberrypi2
    - raspberrypi3
- Add following to your local.conf (including configuration required by meta-mender-core)

        KERNEL_IMAGETYPE = "uImage"

        MENDER_PARTITION_ALIGNMENT_KB = "4096"
        MENDER_BOOT_PART_SIZE_MB = "40"

        do_image_sdimg[depends] += " bcm2835-bootfiles:do_populate_sysroot"

        # raspberrypi files aligned with mender layout requirements
        IMAGE_BOOT_FILES_append = " boot.scr u-boot.bin;${SDIMG_KERNELIMAGE}"
        IMAGE_INSTALL_append = " kernel-image kernel-devicetree"
        IMAGE_FSTYPES_remove += " rpi-sdimg"

- Run `bitbake <image name>`
