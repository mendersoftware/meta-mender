# meta-mender-orangepi

This Yocto layers contains recipes which enables support of building Mender client for Orange Pi boards.

This layer depends on:

    URI: https://github.com/Halolo/orange-pi-distro.git
    branch: master
    revision: HEAD

in addition to `meta-mender` dependencies.

## Build instructions

- Read [the Mender documentation on Building a Mender Yocto image](https://docs.mender.io/Artifacts/Building-Mender-Yocto-image) for Mender specific configuration.

- Set MACHINE to one of the following by using ' . source-me <MACHINE>
    - orange-pi-pc
    - orange-pi-pc-plus
    - orange-pi-zero

- Add following to your local.conf (including configuration required by meta-mender-core)
	# to install correct bootloader to SD card
	MENDER_IMAGE_BOOTLOADER_FILE="u-boot-sunxi-with-spl.bin"

	MENDER_IMAGE_BOOTLOADER_BOOTSECTOR_OFFSET="16"
	
	# add u-boot to boot partition 
	IMAGE_BOOT_FILES ?= "u-boot.bin"

	# enable for all orangepi machines
	MACHINEOVERRIDES =. "orangepi:"

- Run `bitbake <image name>` where options are
     - opipc-minimal (minimal image for orange pi pc)
     - opipcplus-minimal (minimal image for orange pi pc plus)
     - opipc-qt5 (qt5 image for orange pi pc)
     - opiz-minimal (miniaml image for orange pi zero)

