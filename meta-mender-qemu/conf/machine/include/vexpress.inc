include conf/machine/include/arm/arch-armv5-dsp.inc

PREFERRED_PROVIDER_virtual/kernel ?= "linux-yocto"
PREFERRED_VERSION_linux-yocto ?= "4.1%"

SERIAL_CONSOLE = "115200 ttyAMA0"

KERNEL_IMAGETYPE = "zImage"
KERNEL_DEVICETREE = "vexpress-v2p-ca9.dtb"
KERNEL_EXTRA_ARGS += "LOADADDR=${UBOOT_ENTRYPOINT}"

UBOOT_SUFFIX = "bin"
UBOOT_MACHINE = "vexpress_ca9x4_config"
UBOOT_ENTRYPOINT = "0x60800000"
UBOOT_LOADADDRESS = "0x60800000"

UBOOT_ELF ?= "u-boot"
