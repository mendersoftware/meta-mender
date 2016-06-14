# Keep this separately from the rest of the .bb file in case that .bb file is
# overridden from another layer.
require u-boot-mender.inc

DEPENDS = "u-boot"
BOOTENV_SIZE_beaglebone = "0x20000"
BOOTENV_SIZE_vexpress-qemu = "0x40000"

# Configure fw_printenv so that it looks in the right place for the environment.
do_configure_fw_printenv () {
    cat > ${D}${sysconfdir}/fw_env.config <<EOF
/uboot/uboot.env 0x0000 ${BOOTENV_SIZE}
EOF
}
addtask do_configure_fw_printenv before do_package after do_install

