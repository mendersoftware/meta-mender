require initramfs-module-install.inc

do_install:append:mender-efi-boot() {
    install -m 0755 ${UNPACKDIR}/init-install-efi-mender-altered.sh ${D}/init.d/install-efi.sh
}
