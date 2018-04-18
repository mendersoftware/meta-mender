require recipes-bsp/u-boot/u-boot-mender.inc
RPROVIDES_${PN} += "u-boot"
BOOTENV_SIZE = "0x18000"
