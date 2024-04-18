# meta-mender-raspberrypi

This Yocto layers contains recipes which enables support of building Mender client for Raspberry Pi boards.

**NOTE!**. To be able to support update of Linux kernel and DTB, Mender requires these to be installed in the `/boot` directory for each rootfs (normally /dev/mmcblk0p2 and /dev/mmcblk0p3). On the other hand, the Raspberry Pi boot firmware requires that the DTB file is in the same partition as the boot firmware (/dev/mmcbl0p1) and the config.txt file. For now Mender will not use the DTB that is delivered with new artifacts and will continue to boot with the original DTB that was populated using the SDIMG file.

## Dependencies

This layer depends on:

    URI: git://git.yoctoproject.org/meta-raspberrypi
    branch: master
    revision: HEAD

in addition to `meta-mender` dependencies.

## Build instructions

- Read [the Mender documentation on Building a Mender Yocto image](https://docs.mender.io/Artifacts/Building-Mender-Yocto-image) for Mender specific configuration.
- Set MACHINE to one of the following (the list reflects the supported machines of
  `meta-raspberrypi` for the `kirkstone` release branch)
    - raspberrypi
    - raspberrypi0
    - raspberrypi0-wifi
	- raspberrypi0-2w
	- raspberrypi0-2w-64
    - raspberrypi2
    - raspberrypi3
	- raspberrypi3-64
    - raspberrypi-cm
	- raspberrypi-cm3
	- raspberrypi4
	- raspberrypi4-64

- Add following to your local.conf (including configuration required by meta-mender-core)

        RPI_USE_U_BOOT = "1"

        # Having the serial terminal enabled is useful.
        ENABLE_UART = "1"

        # rpi-base.inc removes these as they are normally installed on to the
        # vfat boot partition. To be able to update the Linux kernel Mender
        # uses an image that resides on the root file system and below line
        # ensures that they are installed to /boot
        IMAGE_INSTALL:append = " kernel-image kernel-devicetree"

        # Mender will build an image called `sdimg` which shall be used instead
        # of the `rpi-sdimg`.
        IMAGE_FSTYPES:remove = " rpi-sdimg"

        # Use the same type here as specified in ARTIFACTIMG_FSTYPE to avoid
        # building an unneeded image file.
        SDIMG_ROOTFS_TYPE = "ext4"

        # Reserve more space than the Mender default for the boot partition,
        # as the raspberrypi machines bring some additional things that need
        # to be placed there too
        MENDER_BOOT_PART_SIZE_MB = "64"

        # Configure U-Boot for Raspberry Pi 5
        KERNEL_IMAGETYPE_UBOOT:raspberrypi5 ?= "Image"
        KERNEL_BOOTCMD:raspberrypi5 ?= "booti"
        UBOOT_MACHINE:raspberrypi5 = "rpi_arm64_config"

- Run `bitbake <image name>`
