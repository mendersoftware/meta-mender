# Class for those who want to enable all Mender required features for UBI based
# devices.

MENDER_FEATURES_ENABLE:append = " \
    mender-image \
    mender-image-ubi \
    mender-auth-install \
    mender-update-install \
    mender-systemd \
    mender-ubi \
    mender-uboot \
"

inherit mender-setup
