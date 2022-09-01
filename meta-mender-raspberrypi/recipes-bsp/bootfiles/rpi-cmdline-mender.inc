CMDLINE_ROOTFS:remove = "root=/dev/mmcblk0p2"

do_compile:append() {
    # Modify cmdline.txt after its creation to append root=... parameter
    #
    # We cannot use CMDLINE_ROOTFS:append = " root=\${mender_kernel_root} "
    # because ${...} cannot be properly escaped and do_compile then breaks
    # with bad substitution
    # See https://github.com/agherzan/meta-raspberrypi/blob/master/recipes-bsp/bootfiles/rpi-cmdline.bb

    sed -i 's,$, root=\${mender_kernel_root},' "${WORKDIR}/cmdline.txt"
}
