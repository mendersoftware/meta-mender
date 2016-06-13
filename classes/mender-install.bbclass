# Class for those who want to install the Mender client into the image.

PREFERRED_VERSION_go_cross = "1.6%"

# Add support for systemd
#
# Note that a very common error with systemd is that the system hangs during the
# boot process while looking for devices. This is almost always because the
# kernel feature CONFIG_FHANDLE is not enabled.
DISTRO_FEATURES_append = " systemd"
VIRTUAL-RUNTIME_init_manager = "systemd"
DISTRO_FEATURES_BACKFILL_CONSIDERED = "sysvinit"
VIRTUAL-RUNTIME_initscripts = ""

IMAGE_INSTALL_append = " mender ca-certificates"

# The storage device that holds the device partitions.
MENDER_STORAGE_DEVICE ?= "/dev/mmcblk0"

# The base name of the devices that hold individual partitions.
# This is often MENDER_STORAGE_DEVICE + "p".
MENDER_STORAGE_DEVICE_BASE ?= "/dev/mmcblk0p"

# The partition number holding the boot partition.
MENDER_BOOT_PART ?= "${MENDER_STORAGE_DEVICE_BASE}1"

# The numbers of the two rootfs partitions in the A/B partition layout.
MENDER_ROOTFS_PART_A ?= "${MENDER_STORAGE_DEVICE_BASE}2"
MENDER_ROOTFS_PART_B ?= "${MENDER_STORAGE_DEVICE_BASE}3"

# The partition number holding the data partition.
MENDER_DATA_PART ?= "${MENDER_STORAGE_DEVICE_BASE}5"
