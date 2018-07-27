# Class for those who want to enable all Mender required features.

MENDER_FEATURES_ENABLE_append = " \
    mender-image \
    mender-install \
    mender-systemd \
"

MENDER_FEATURES_ENABLE_append_arm = " mender-image-sd mender-uboot"
MENDER_FEATURES_ENABLE_append_aarch64 = " mender-image-sd mender-uboot"

MENDER_FEATURES_ENABLE_append_x86 = " mender-image-uefi mender-grub"
MENDER_FEATURES_ENABLE_append_x86-64 = " mender-image-uefi mender-grub"
