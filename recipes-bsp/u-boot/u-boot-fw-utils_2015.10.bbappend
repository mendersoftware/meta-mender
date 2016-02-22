# Keep this separately from the rest of the .bb file in case that .bb file is
# overridden from another layer.

DEPENDS = "u-boot"

FILESEXTRAPATHS_prepend := "${THISDIR}/files:"
SRC_URI_vexpress-qemu += "file://0001-Enable-boot-code-specifically-for-the-U-Boot-QEMU-sc.patch"

BOOTENV_SIZE_beaglebone = "0x20000"
BOOTENV_SIZE_vexpress-qemu = "0x40000"

# Configure fw_printenv so that it looks in the right place for the environment.
do_configure_fw_printenv () {
    cat > ${D}${sysconfdir}/fw_env.config <<EOF
/u-boot/uboot.env 0x0000 ${BOOTENV_SIZE}
EOF
}
addtask do_configure_fw_printenv before do_package after do_install

