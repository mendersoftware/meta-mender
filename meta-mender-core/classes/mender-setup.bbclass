inherit mender-helpers

# ------------------------------ CONFIGURATION ---------------------------------

# The storage device that holds the device partitions.
MENDER_STORAGE_DEVICE ??= "${MENDER_STORAGE_DEVICE_DEFAULT}"
MENDER_STORAGE_DEVICE_DEFAULT = "/dev/mmcblk0"

# The base name of the devices that hold individual partitions.
# This is often MENDER_STORAGE_DEVICE + "p".
MENDER_STORAGE_DEVICE_BASE ??= "${MENDER_STORAGE_DEVICE_BASE_DEFAULT}"
MENDER_STORAGE_DEVICE_BASE_DEFAULT = "${MENDER_STORAGE_DEVICE}p"

# The partition number holding the boot partition.
MENDER_BOOT_PART ??= "${MENDER_BOOT_PART_DEFAULT}"
MENDER_BOOT_PART_DEFAULT = "${MENDER_STORAGE_DEVICE_BASE}1"

# The numbers of the two rootfs partitions in the A/B partition layout.
MENDER_ROOTFS_PART_A ??= "${MENDER_ROOTFS_PART_A_DEFAULT}"
MENDER_ROOTFS_PART_A_DEFAULT = "${MENDER_STORAGE_DEVICE_BASE}2"
MENDER_ROOTFS_PART_B ??= "${MENDER_ROOTFS_PART_B_DEFAULT}"
MENDER_ROOTFS_PART_B_DEFAULT = "${MENDER_STORAGE_DEVICE_BASE}3"

# The names of the two rootfs partitions in the A/B partition layout. By default
# it is the same name as MENDER_ROOTFS_PART_A and MENDER_ROOTFS_B
MENDER_ROOTFS_PART_A_NAME ??= "${MENDER_ROOTFS_PART_A_NAME_DEFAULT}"
MENDER_ROOTFS_PART_A_NAME_DEFAULT = "${MENDER_ROOTFS_PART_A}"
MENDER_ROOTFS_PART_B_NAME ??= "${MENDER_ROOTFS_PART_B_NAME_DEFAULT}"
MENDER_ROOTFS_PART_B_NAME_DEFAULT = "${MENDER_ROOTFS_PART_B}"

# The partition number holding the data partition.
MENDER_DATA_PART ??= "${MENDER_DATA_PART_DEFAULT}"
MENDER_DATA_PART_DEFAULT = "${MENDER_STORAGE_DEVICE_BASE}4"

# The name of of the MTD part holding your UBI volumes.
MENDER_MTD_UBI_DEVICE_NAME ??= "${MENDER_MTD_UBI_DEVICE_NAME_DEFAULT}"
MENDER_MTD_UBI_DEVICE_NAME_DEFAULT = ""

# Filesystem type of data partition. This configuration is used in fstab. Most
# filesystems can be auto detected, but some can not and hence we allow the
# user to override this.
MENDER_DATA_PART_FSTYPE ??= "${MENDER_DATA_PART_FSTYPE_DEFAULT}"
MENDER_DATA_PART_FSTYPE_DEFAULT = "auto"
MENDER_BOOT_PART_FSTYPE ??= "${MENDER_BOOT_PART_FSTYPE_DEFAULT}"
MENDER_BOOT_PART_FSTYPE_DEFAULT = "auto"

# Device type of device when making an initial partitioned image.
MENDER_DEVICE_TYPE ??= "${MENDER_DEVICE_TYPE_DEFAULT}"
MENDER_DEVICE_TYPE_DEFAULT = "${MACHINE}"

# Space separated list of device types compatible with the built update.
MENDER_DEVICE_TYPES_COMPATIBLE ??= "${MENDER_DEVICE_TYPES_COMPATIBLE_DEFAULT}"
MENDER_DEVICE_TYPES_COMPATIBLE_DEFAULT = "${MENDER_DEVICE_TYPE}"

# Upstream poky changed their Beaglebone machine name from "beaglebone" to
# "beaglebone-yocto". Add the old name to the list of compatible devices, so
# people can upgrade.
MENDER_DEVICE_TYPES_COMPATIBLE_DEFAULT_append_beaglebone-yocto = " beaglebone"

# Total size of the medium that mender sdimg will be written to. The size of
# rootfs partition will be calculated automatically by subtracting the size of
# boot and data partitions along with some predefined overhead (see
# MENDER_PARTITIONING_OVERHEAD_KB).
MENDER_STORAGE_TOTAL_SIZE_MB ??= "${MENDER_STORAGE_TOTAL_SIZE_MB_DEFAULT}"
MENDER_STORAGE_TOTAL_SIZE_MB_DEFAULT = "1024"

# Optional location where a directory can be specified with content that should
# be included on the data partition. Some of Mender's own files will be added to
# this (e.g. OpenSSL certificates).
MENDER_DATA_PART_DIR ??= "${MENDER_DATA_PART_DIR_DEFAULT}"
MENDER_DATA_PART_DIR_DEFAULT = ""

# Size of the data partition, which is preserved across updates.
MENDER_DATA_PART_SIZE_MB ??= "${MENDER_DATA_PART_SIZE_MB_DEFAULT}"
MENDER_DATA_PART_SIZE_MB_DEFAULT = "128"

# Size of the first (FAT) partition, that contains the bootloader
MENDER_BOOT_PART_SIZE_MB ??= "${MENDER_BOOT_PART_SIZE_MB_DEFAULT}"
MENDER_BOOT_PART_SIZE_MB_DEFAULT = "16"

# For performance reasons, we try to align the partitions to the SD card's erase
# block (PEB). It is impossible to know this information with certainty, but one
# way to find out is to run the "flashbench" tool on your SD card and study the
# results. If you do, feel free to override this default.
#
# 8MB alignment is a safe setting that might waste some space if the erase block
# is smaller.
MENDER_PARTITION_ALIGNMENT_KB ??= "${MENDER_PARTITION_ALIGNMENT_KB_DEFAULT}"
MENDER_PARTITION_ALIGNMENT_KB_DEFAULT = "8192"

# The reserved space between the partition table and the first partition.
# Most people don't need to set this, and it will be automatically overridden
# by mender-uboot distro feature.
MENDER_STORAGE_RESERVED_RAW_SPACE ??= "${MENDER_STORAGE_RESERVED_RAW_SPACE_DEFAULT}"
MENDER_STORAGE_RESERVED_RAW_SPACE_DEFAULT = "0"

# The interface to load partitions from. This is normally empty, in which case
# it is deduced from MENDER_STORAGE_DEVICE. Only use this if the interface
# cannot be deduced from MENDER_STORAGE_DEVICE.
MENDER_UBOOT_STORAGE_INTERFACE ??= "${MENDER_UBOOT_STORAGE_INTERFACE_DEFAULT}"
MENDER_UBOOT_STORAGE_INTERFACE_DEFAULT = ""

# The device number of the interface to load partitions from. This is normally
# empty, in which case it is deduced from MENDER_STORAGE_DEVICE. Only use this
# if the indexing of devices is different in U-Boot and in the Linux kernel.
MENDER_UBOOT_STORAGE_DEVICE ??= "${MENDER_UBOOT_STORAGE_DEVICE_DEFAULT}"
MENDER_UBOOT_STORAGE_DEVICE_DEFAULT = ""

# This will be embedded into the boot sector, or close to the boot sector, where
# exactly depends on the offset variable. Since it is a machine specific
# setting, the default value is an empty string.
IMAGE_BOOTLOADER_FILE ??= "${MENDER_IMAGE_BOOTLOADER_FILE_DEFAULT}"
MENDER_IMAGE_BOOTLOADER_FILE_DEFAULT = ""

# Offset of bootloader, in sectors (512 bytes).
IMAGE_BOOTLOADER_BOOTSECTOR_OFFSET ??= "${IMAGE_BOOTLOADER_BOOTSECTOR_OFFSET_DEFAULT}"
IMAGE_BOOTLOADER_BOOTSECTOR_OFFSET_DEFAULT = "2"

# --------------------------- END OF CONFIGURATION -----------------------------

IMAGE_INSTALL_append = " mender"
IMAGE_CLASSES += "mender-part-images mender-ubimg mender-artifactimg"

# MENDER_FEATURES_ENABLE and MENDER_FEATURES_DISABLE map to
# DISTRO_FEATURES_BACKFILL and DISTRO_FEATURES_BACKFILL_CONSIDERED,
# respectively.
DISTRO_FEATURES_BACKFILL_append = " ${MENDER_FEATURES_ENABLE}"
DISTRO_FEATURES_BACKFILL_CONSIDERED_append = " ${MENDER_FEATURES_DISABLE}"

python() {
    # Add all possible Mender features here. This list is here to have an
    # authoritative list of all distro features that Mender provides.
    # Each one will also define the same string in OVERRIDES.
    mender_features = {

        # Install of Mender, with the minimum components. This includes no
        # references to specific partition layouts.
        'mender-install',

        # Include components for Mender-partitioned images. This will create
        # files that rely on the Mender partition layout.
        'mender-image',

        # Include components for generating an SD image.
        'mender-image-sd',

        # Include components for generating a UBI image.
        'mender-image-ubi',

        # Include Mender as a systemd service.
        'mender-systemd',

        # Enable Mender configuration specific to UBI.
        'mender-ubi',

        # Use Mender together with U-Boot.
        'mender-uboot',
    }

    mfe = d.getVar('MENDER_FEATURE_ENABLE')
    mfe = mfe.split() if mfe is not None else []
    mfd = d.getVar('MENDER_FEATURE_DISABLE')
    mfd = mfd.split() if mfd is not None else []
    for feature in mfe + mfd:
        if not feature.startswith('mender-'):
            bb.fatal("%s in MENDER_FEATURE_ENABLE or MENDER_FEATURE_DISABLE is not a Mender feature."
                     % feature)

    for feature in d.getVar('DISTRO_FEATURES').split():
        if feature.startswith("mender-"):
            if feature not in mender_features:
                bb.fatal("%s from MENDER_FEATURE_ENABLE or DISTRO_FEATURES is not a valid Mender feature."
                         % feature)
            d.setVar('OVERRIDES_append', ':%s' % feature)
}

python() {
    if d.getVar('MENDER_PARTITION_ALIGNMENT_MB', True):
        bb.fatal("MENDER_PARTITION_ALIGNMENT_MB is deprecated. Please define MENDER_PARTITION_ALIGNMENT_KB instead.")
}


def mender_get_bytes_with_unit(bytes):
    if bytes % 1048576 == 0:
        return "%dm" % (bytes / 1048576)
    if bytes % 1024 == 0:
        return "%dk" % (bytes / 1024)
    return "%d" % bytes

# Including these does not mean that all these features will be enabled, just
# that their configuration will be considered. Use DISTRO_FEATURES to enable and
# disable features.
include mender-setup-image.inc
include mender-setup-install.inc
include mender-setup-systemd.inc
include mender-setup-ubi.inc
include mender-setup-uboot.inc
