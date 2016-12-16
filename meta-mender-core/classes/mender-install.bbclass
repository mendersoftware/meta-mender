# Class for those who want to install the Mender client into the image.

# ------------------------------ CONFIGURATION ---------------------------------

# The storage device that holds the device partitions.
MENDER_STORAGE_DEVICE ?= "/dev/mmcblk0"

# The interface to load partitions from. This is normally empty, in which case
# it is deduced from MENDER_STORAGE_DEVICE. Only use this if the interface
# cannot be deduced from MENDER_STORAGE_DEVICE.
MENDER_UBOOT_STORAGE_INTERFACE ?= ""

# The device number of the interface to load partitions from. This is normally
# empty, in which case it is deduced from MENDER_STORAGE_DEVICE. Only use this
# if the indexing of devices is different in U-Boot and in the Linux kernel.
MENDER_UBOOT_STORAGE_DEVICE ?= ""

# The base name of the devices that hold individual partitions.
# This is often MENDER_STORAGE_DEVICE + "p".
MENDER_STORAGE_DEVICE_BASE ?= "${MENDER_STORAGE_DEVICE}p"

# The partition number holding the boot partition.
MENDER_BOOT_PART ?= "${MENDER_STORAGE_DEVICE_BASE}1"

# The numbers of the two rootfs partitions in the A/B partition layout.
MENDER_ROOTFS_PART_A ?= "${MENDER_STORAGE_DEVICE_BASE}2"
MENDER_ROOTFS_PART_B ?= "${MENDER_STORAGE_DEVICE_BASE}3"

# The partition number holding the data partition.
MENDER_DATA_PART ?= "${MENDER_STORAGE_DEVICE_BASE}5"

# Device type of device when making an initial partitioned image.
MENDER_DEVICE_TYPE ?= "${MACHINE}"

# Space separated list of device types compatible with the built update.
MENDER_DEVICE_TYPES_COMPATIBLE ?= "${MACHINE}"

# Total size of the medium that mender sdimg will be written to. The size of
# rootfs partition will be calculated automatically by subtracting the size of
# boot and data partitions along with some predefined overhead (see
# MENDER_PARTITIONING_OVERHEAD_MB).
MENDER_STORAGE_TOTAL_SIZE_MB ?= "1024"

# Optional location where a directory can be specified with content that should
# be included on the data partition. Some of Mender's own files will be added to
# this (e.g. OpenSSL certificates).
MENDER_DATA_PART_DIR ?= ""

# Size of the data partition, which is preserved across updates.
MENDER_DATA_PART_SIZE_MB ?= "128"

# Size of the first (FAT) partition, that contains the bootloader
MENDER_BOOT_PART_SIZE_MB ?= "16"

# For performance reasons, we try to align the partitions to the SD
# card's erase block. It is impossible to know this information with
# certainty, but one way to find out is to run the "flashbench" tool on
# your SD card and study the results. If you do, feel free to override
# this default.
#
# 8MB alignment is a safe setting that might waste some space if the
# erase block is smaller.
MENDER_PARTITION_ALIGNMENT_MB ?= "8"

# --------------------------- END OF CONFIGURATION -----------------------------


PREFERRED_VERSION_go_cross = "1.6%"

IMAGE_INSTALL_append = " \
    mender \
    ca-certificates \
    mender-artifact-info \
    "
