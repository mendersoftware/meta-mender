# meta-mender-raspberrypi

This Yocto layers contains recipes which enables support of building Mender client for Raspberry Pi boards.

**NOTE!**. To be able to support update of Linux kernel and DTB these are installed to `/boot` on rootfs. This breaks support of user configurations based on `config.txt` because the Raspberry Pi boot firmware requires that the DTB file is in the same partition as the boot firmware files (mmcblk0p1). Boot firmware normally patches the DTB file based on configurations in `config.txt`.

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

        IMAGE_DEPENDS_sdimg += " bcm2835-bootfiles"

        # raspberrypi files aligned with mender layout requirements
        IMAGE_BOOT_FILES_append = " boot.scr u-boot.bin;${SDIMG_KERNELIMAGE}"
        IMAGE_INSTALL_append = " kernel-image kernel-devicetree"

- Run `bitbake <image name>`
