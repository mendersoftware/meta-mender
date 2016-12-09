run mender_setup
setenv fdtfile bcm2708-rpi-b.dtb
setenv bootargs earlyprintk console=tty0 console=ttyAMA0,115200 root=${mender_kernel_root} rootfstype=ext4 rootwait noinitrd
mmc dev ${mender_uboot_dev}
load ${mender_uboot_root} ${kernel_addr_r} /boot/uImage
load ${mender_uboot_root} ${fdt_addr_r} /boot/${fdtfile}
bootm ${kernel_addr_r} - ${fdt_addr_r}
run mender_try_to_recover
