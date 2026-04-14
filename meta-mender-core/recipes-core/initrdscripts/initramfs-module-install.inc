FILESEXTRAPATHS:prepend:mender-efi-boot := "${THISDIR}/files:"

SRC_URI:append:mender-efi-boot = " file://init-install-efi-mender.sh "

do_install:append:mender-efi-boot() {
    # Overwrite the version of this file provided by upstream
    sed -e 's#[@]MENDER_STORAGE_DEVICE[@]#${MENDER_STORAGE_DEVICE}#' ${UNPACKDIR}/init-install-efi-mender.sh > ${WORKDIR}/init-install-efi-mender-altered.sh
}
