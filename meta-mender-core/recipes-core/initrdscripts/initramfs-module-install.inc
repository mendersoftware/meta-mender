FILESEXTRAPATHS_prepend_mender-efi-boot := "${THISDIR}/files:"

SRC_URI_append_mender-efi-boot = " file://init-install-efi-mender.sh "

do_install_append_mender-efi-boot() {
    # Overwrite the version of this file provided by upstream
    sed -e 's#[@]MENDER_STORAGE_DEVICE[@]#${MENDER_STORAGE_DEVICE}#' ${WORKDIR}/init-install-efi-mender.sh > init-install-efi-mender-altered.sh
}
