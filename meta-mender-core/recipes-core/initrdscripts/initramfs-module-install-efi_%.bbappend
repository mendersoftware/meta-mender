require initramfs-module-install.inc

do_install:append:mender-efi-boot() {
    install -m 0755 ${WORKDIR}/init-install-efi-mender-altered.sh ${D}/init.d/install-efi.sh
}
