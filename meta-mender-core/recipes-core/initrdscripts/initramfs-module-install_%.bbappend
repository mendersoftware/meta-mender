require initramfs-module-install.inc

do_install_append() {
    install -m 0755 ${WORKDIR}/init-install-efi-mender-altered.sh ${D}/init.d/install.sh
}
