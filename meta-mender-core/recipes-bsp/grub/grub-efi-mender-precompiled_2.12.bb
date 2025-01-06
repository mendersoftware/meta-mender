require grub-efi-mender-precompiled.inc

# Grub version 2.12
GRUB_MENDER_GRUBENV_REV = "089c619e3b52b95fd14dc664cf4f6c243c840b94"

SRC_URI = " \
    ${GRUB_MENDER_GRUBENV_SRC_URI} \
    ${URL_BASE}/${PV}-grub-mender-grubenv-${GRUB_MENDER_GRUBENV_REV}/${HOST_ARCH}/grub-efi-${EFI_BOOT_IMAGE};md5sum=3cdc5695de01804044e3b5606a9dc889 \
    ${URL_BASE}/${PV}-grub-mender-grubenv-${GRUB_MENDER_GRUBENV_REV}/${HOST_ARCH}/grub-editenv;md5sum=a7191248afae6f6ae680bf51b91e8d76 \
"
