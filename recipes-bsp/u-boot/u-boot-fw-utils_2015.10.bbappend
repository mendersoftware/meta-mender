# Keep this separately from the rest of the .bb file in case that .bb file is
# overridden from another layer.

inherit deploy

FILESEXTRAPATHS_prepend := "${THISDIR}/files:"
SRC_URI += "file://0001-Enable-boot-code-specifically-for-the-U-Boot-QEMU-sc.patch"

# Configure fw_printenv so that it looks in the right place for the environment.
do_configure_fw_printenv () {
    cat > ${D}${sysconfdir}/fw_env.config <<EOF
/u-boot/uboot.env 0x0000 0x40000
EOF
}
addtask do_configure_fw_printenv before do_package after do_install

