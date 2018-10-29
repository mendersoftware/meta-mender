# Class for those who want to enable all Mender required features.

MENDER_FEATURES_ENABLE_append = " \
    mender-grub \
    mender-image \
    ${_MENDER_IMAGE_TYPE_DEFAULT} \
    mender-install \
    mender-systemd \
"

_MENDER_IMAGE_TYPE_DEFAULT = "mender-image-uefi"

# Beaglebone reads the first VFAT partition and only understands MBR partition
# table. Even though this is a slight violation of the UEFI spec, change to that
# for Beaglebone.
_MENDER_IMAGE_TYPE_DEFAULT_beaglebone-yocto = "mender-image-sd"
