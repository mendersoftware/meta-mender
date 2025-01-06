require grub-efi-mender-precompiled.inc

# Grub version 2.04
GRUB_MENDER_GRUBENV_REV = "eeb7ebd9e6558cf6bbe661b4f2e4e45d52efa305"

SRC_URI = " \
    ${GRUB_MENDER_GRUBENV_SRC_URI} \
    ${URL_BASE}/${PV}-grub-mender-grubenv-${GRUB_MENDER_GRUBENV_REV}/${HOST_ARCH}/grub-efi-${EFI_BOOT_IMAGE};md5sum=63c8f8570b763b59dd2a26f372e03155 \
    ${URL_BASE}/${PV}-grub-mender-grubenv-${GRUB_MENDER_GRUBENV_REV}/${HOST_ARCH}/grub-editenv;md5sum=2c5e943a0acc4a6bd385a9d3f72b637b \
"
