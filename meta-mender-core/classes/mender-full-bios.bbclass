# Class for those who want to enable all Mender required features for BIOS based
# boards.

inherit mender-setup

MENDER_FEATURES_ENABLE:append = " \
    mender-image \
    mender-client-install \
    mender-systemd \
"

MENDER_FEATURES_ENABLE:append:x86 = " mender-image-bios mender-grub mender-bios"
MENDER_FEATURES_ENABLE:append:x86-64 = " mender-image-bios mender-grub mender-bios"
