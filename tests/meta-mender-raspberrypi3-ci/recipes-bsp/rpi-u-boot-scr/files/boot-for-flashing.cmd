fdt addr ${fdt_addr} && fdt get value bootargs /chosen bootargs
load usb 0 ${kernel_addr_r} /kernel7.img
bootz ${kernel_addr_r} - ${fdt_addr}
