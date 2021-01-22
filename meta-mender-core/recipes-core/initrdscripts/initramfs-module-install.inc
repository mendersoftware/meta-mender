FILESEXTRAPATHS_prepend := "${THISDIR}/files:"

SRC_URI += "file://init-install-efi-mender.sh"

do_install_append() {
    # Overwrite the version of this file provided by upstream
    sed -e 's#[@]MENDER_STORAGE_DEVICE[@]#${MENDER_STORAGE_DEVICE}#' ${WORKDIR}/init-install-efi-mender.sh > init-install-efi-mender-altered.sh
}
