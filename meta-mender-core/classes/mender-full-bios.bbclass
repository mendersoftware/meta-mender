# Class for those who want to enable all Mender required features for BIOS based
# boards.

MENDER_FEATURES_ENABLE_append = " \
    mender-image \
    mender-client-install \
    mender-systemd \
"

MENDER_FEATURES_ENABLE_append_x86 = " mender-image-bios mender-grub mender-bios"
MENDER_FEATURES_ENABLE_append_x86-64 = " mender-image-bios mender-grub mender-bios"
