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

# --------------------------- END OF CONFIGURATION -----------------------------


PREFERRED_VERSION_go_cross = "1.6%"

IMAGE_INSTALL_append = " \
    mender \
    ca-certificates \
    mender-artifact \
    "
