ARTIFACTIMG_FSTYPE_DEFAULT_mender-ubi = "ubifs"

MENDER_STORAGE_DEVICE_DEFAULT_mender-ubi = "ubi0"

# The base name of the devices that hold individual volumes.
MENDER_STORAGE_DEVICE_BASE_DEFAULT_mender-ubi = "${MENDER_STORAGE_DEVICE}_"

# The numbers of the two rootfs partitions in the A/B partition layout.
MENDER_ROOTFS_PART_A_DEFAULT_mender-ubi = "${MENDER_STORAGE_DEVICE_BASE}0"
MENDER_ROOTFS_PART_B_DEFAULT_mender-ubi = "${MENDER_STORAGE_DEVICE_BASE}1"

# The partition number holding the data partition.
MENDER_DATA_PART_DEFAULT_mender-ubi = "${MENDER_STORAGE_DEVICE_BASE}2"
MENDER_DATA_PART_FSTYPE_DEFAULT_mender-ubi = "ubifs"

# u-boot command ubifsmount requires volume name as the only argument
# and hence we need to keep track of that since we load kernel/dtb from
# rootfs part
#
# It also needs the volume index e.g.
# ubifsmount ubi0:rootfsa
MENDER_ROOTFS_PART_A_NAME_DEFAULT_mender-ubi = "${MENDER_STORAGE_DEVICE}:rootfsa"
MENDER_ROOTFS_PART_B_NAME_DEFAULT_mender-ubi = "${MENDER_STORAGE_DEVICE}:rootfsb"

# The name of of the MTD part holding your UBI volumes.
MENDER_MTD_UBI_DEVICE_NAME_DEFAULT_mender-ubi = "ubi"

# Boot part is not used when building UBI image.
MENDER_BOOT_PART_DEFAULT_mender-ubi = ""
MENDER_BOOT_PART_SIZE_MB_DEFAULT_mender-ubi = "0"

# These are not applicable when building UBI image.
MENDER_UBOOT_STORAGE_DEVICE_DEFAULT_mender-ubi = "dummy"
MENDER_UBOOT_STORAGE_INTERFACE_DEFAULT_mender-ubi = "dummy"
