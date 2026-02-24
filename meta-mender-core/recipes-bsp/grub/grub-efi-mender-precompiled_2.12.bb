require grub-efi-mender-precompiled.inc

# Grub version 2.12
GRUB_MENDER_GRUBENV_REV = "d7c3ec217e281727f56c3651799f805637cb2cda"

SRC_URI = " \
    ${GRUB_MENDER_GRUBENV_SRC_URI} \
    ${URL_BASE}/${PV}-grub-mender-grubenv-${GRUB_MENDER_GRUBENV_REV}/${HOST_ARCH}/grub-efi-${EFI_BOOT_IMAGE};md5sum=82551c65068ba41bbd32a27acb589745 \
    ${URL_BASE}/${PV}-grub-mender-grubenv-${GRUB_MENDER_GRUBENV_REV}/${HOST_ARCH}/grub-editenv;md5sum=9828f74daaeaae27776e7040c7f29c65 \
"
