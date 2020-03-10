# Class for those who want to enable all Mender required features.

MENDER_FEATURES_ENABLE_append = " \
    ${_MENDER_BOOTLOADER_DEFAULT} \
    mender-image \
    ${_MENDER_IMAGE_TYPE_DEFAULT} \
    mender-client-install \
    mender-systemd \
    ${_MENDER_GROWFS_DATA_DEFAULT} \
"

_MENDER_IMAGE_TYPE_DEFAULT ?= "mender-image-uefi"
_MENDER_BOOTLOADER_DEFAULT ?= "mender-grub"

_MENDER_GROWFS_DATA_DEFAULT ?= "${@'' if d.getVar('MENDER_EXTRA_PARTS') else 'mender-growfs-data'}"

# Beaglebone reads the first VFAT partition and only understands MBR partition
# table. Even though this is a slight violation of the UEFI spec, change to that
# for Beaglebone.
_MENDER_IMAGE_TYPE_DEFAULT_beaglebone-yocto = "mender-image-sd"
