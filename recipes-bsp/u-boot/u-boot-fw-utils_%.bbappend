# Keep this separately from the rest of the .bb file in case that .bb file is
# overridden from another layer.
require u-boot-mender.inc

DEPENDS = "u-boot"

do_compile_append() {
    # create fw_env.config file
    cat > ${WORKDIR}/fw_env.config <<EOF
/uboot/uboot.env 0x0000 ${BOOTENV_SIZE}
EOF
}

do_install_append() {
    install -m 0644 ${WORKDIR}/fw_env.config ${D}${sysconfdir}/fw_env.config
}
