FILESEXTRAPATHS_prepend := "${THISDIR}/files:"

SRC_URI_append_beaglebone = " file://0001-beaglebone-mender-specific-configuration.patch \
                              file://uEnv.txt"

SRC_URI_append_vexpress-qemu = " file://0001-Enable-boot-code-specifically-for-the-U-Boot-QEMU-sc.patch \
                                 file://0003-Add-kernel-panic-option-to-vexpress-boot-arguments.patch"

SRC_URI_append = " file://0002-Add-missing-header-which-fails-on-recent-GCC.patch"

