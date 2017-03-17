ARTIFACTIMG_FSTYPE ?= "ubifs"

MENDER_STORAGE_DEVICE ?= "ubi0"

# The base name of the devices that hold individual volumes.
MENDER_STORAGE_DEVICE_BASE ?= "${MENDER_STORAGE_DEVICE}_"

# The numbers of the two rootfs partitions in the A/B partition layout.
MENDER_ROOTFS_PART_A ?= "${MENDER_STORAGE_DEVICE_BASE}0"
MENDER_ROOTFS_PART_B ?= "${MENDER_STORAGE_DEVICE_BASE}1"

# The partition number holding the data partition.
MENDER_DATA_PART ?= "${MENDER_STORAGE_DEVICE_BASE}2"
MENDER_DATA_FSTYPE ?= "ubifs"

# u-boot command ubifsmount requires volume name as the only argument
# and hence we need to keep track of that since we load kernel/dtb from
# rootfs part
#
# It also needs the volume index e.g.
# ubifsmount ubi0:rootfsa
MENDER_ROOTFS_PART_A_NAME ?= "${MENDER_STORAGE_DEVICE}:rootfsa"
MENDER_ROOTFS_PART_B_NAME ?= "${MENDER_STORAGE_DEVICE}:rootfsb"

# The name of of the MTD part holding your UBI volumes.
MENDER_MTD_UBI_DEVICE_NAME ?= "ubi"

# Boot part is not used when building UBI image.
MENDER_BOOT_PART ?= ""
MENDER_BOOT_PART_SIZE_MB ?= "0"

# These are not applicable when building UBI image.
MENDER_UBOOT_STORAGE_DEVICE ?= "dummy"
MENDER_UBOOT_STORAGE_INTERFACE ?= "dummy"
