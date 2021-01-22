require initramfs-module-install.inc

do_install_append_mender-grub() {
    install -m 0755 ${WORKDIR}/init-install-efi-mender-altered.sh ${D}/init.d/install-efi.sh
}
