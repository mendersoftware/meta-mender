inherit mender-helpers

# ------------------------------ CONFIGURATION ---------------------------------

# The machine to be used for Mender.
# For some reason 'bitbake -e' does not report the MACHINE value so
# we use this as a proxy in case it is not available when needed.
export MENDER_MACHINE = "${MACHINE}"
BB_HASHBASE_WHITELIST += "MENDER_MACHINE"

# The storage device that holds the device partitions.
MENDER_STORAGE_DEVICE ??= "${MENDER_STORAGE_DEVICE_DEFAULT}"
MENDER_STORAGE_DEVICE_DEFAULT = "/dev/mmcblk0"

# The base name of the devices that hold individual partitions.
# This is often MENDER_STORAGE_DEVICE + "p".
MENDER_STORAGE_DEVICE_BASE ??= "${MENDER_STORAGE_DEVICE_BASE_DEFAULT}"
def mender_linux_partition_base(dev):
    import re
    if re.match("^/dev/[sh]d[a-z]", dev):
        return dev
    else:
        return "%sp" % dev
MENDER_STORAGE_DEVICE_BASE_DEFAULT = "${@mender_linux_partition_base('${MENDER_STORAGE_DEVICE}')}"

# The partition number holding the boot partition.
MENDER_BOOT_PART_NUMBER ??= "${MENDER_BOOT_PART_NUMBER_DEFAULT}"
MENDER_BOOT_PART_NUMBER_DEFAULT = "1"

# The string path of the boot partition.
MENDER_BOOT_PART ??= "${MENDER_BOOT_PART_DEFAULT}"
MENDER_BOOT_PART_DEFAULT = "${MENDER_STORAGE_DEVICE_BASE}${MENDER_BOOT_PART_NUMBER}"

# The numbers of the two rootfs partitions in the A/B partition layout.
MENDER_ROOTFS_PART_A_NUMBER ??= "${MENDER_ROOTFS_PART_A_NUMBER_DEFAULT}"
MENDER_ROOTFS_PART_A_NUMBER_DEFAULT = "${@bb.utils.contains('MENDER_BOOT_PART_SIZE_MB', '0', '1', '2', d)}"
MENDER_ROOTFS_PART_B_NUMBER ??= "${MENDER_ROOTFS_PART_B_NUMBER_DEFAULT}"
MENDER_ROOTFS_PART_B_NUMBER_DEFAULT = "${@bb.utils.contains('MENDER_BOOT_PART_SIZE_MB', '0', '2', '3', d)}"

# The string path of the two rootfs partitions in the A/B partition layout
MENDER_ROOTFS_PART_A ??= "${MENDER_ROOTFS_PART_A_DEFAULT}"
MENDER_ROOTFS_PART_A_DEFAULT = "${MENDER_STORAGE_DEVICE_BASE}${MENDER_ROOTFS_PART_A_NUMBER}"
MENDER_ROOTFS_PART_B ??= "${MENDER_ROOTFS_PART_B_DEFAULT}"
MENDER_ROOTFS_PART_B_DEFAULT = "${MENDER_STORAGE_DEVICE_BASE}${MENDER_ROOTFS_PART_B_NUMBER}"

# The names of the two rootfs partitions in the A/B partition layout. By default
# it is the same name as MENDER_ROOTFS_PART_A and MENDER_ROOTFS_B
MENDER_ROOTFS_PART_A_NAME ??= "${MENDER_ROOTFS_PART_A_NAME_DEFAULT}"
MENDER_ROOTFS_PART_A_NAME_DEFAULT = "${MENDER_ROOTFS_PART_A}"
MENDER_ROOTFS_PART_B_NAME ??= "${MENDER_ROOTFS_PART_B_NAME_DEFAULT}"
MENDER_ROOTFS_PART_B_NAME_DEFAULT = "${MENDER_ROOTFS_PART_B}"

# The partition number holding the data partition.
MENDER_DATA_PART_NUMBER ??= "${MENDER_DATA_PART_NUMBER_DEFAULT}"
MENDER_DATA_PART_NUMBER_DEFAULT = "${@mender_get_data_part_num(d)}"

# The string path of the the data partition.
MENDER_DATA_PART ??= "${MENDER_DATA_PART_DEFAULT}"
MENDER_DATA_PART_DEFAULT = "${MENDER_STORAGE_DEVICE_BASE}${MENDER_DATA_PART_NUMBER}"

# The name of of the MTD part holding your UBI volumes.
MENDER_MTD_UBI_DEVICE_NAME ??= "${MENDER_MTD_UBI_DEVICE_NAME_DEFAULT}"
MENDER_MTD_UBI_DEVICE_NAME_DEFAULT = ""

# Filesystem type of data partition. Used for both FS generation and fstab construction
# Leave as default (auto) to generate a partition using the same Filesystem as 
# the rootfs ($ARTIFACTIMG_FSTYPE) and set the fstab to auto-detect the partition type
# Set to a known filesystem to generate the partition using that type
MENDER_DATA_PART_FSTYPE ??= "${MENDER_DATA_PART_FSTYPE_DEFAULT}"
MENDER_DATA_PART_FSTYPE_DEFAULT = "auto"

# Filesystem type of data partition to generate. Used only for FS generation
# Typically you'll be best off setting MENDER_DATA_PART_FSTYPE instead
MENDER_DATA_PART_FSTYPE_TO_GEN ??= "${MENDER_DATA_PART_FSTYPE_TO_GEN_DEFAULT}"
MENDER_DATA_PART_FSTYPE_TO_GEN_DEFAULT = "${@bb.utils.contains('MENDER_DATA_PART_FSTYPE', 'auto', '${ARTIFACTIMG_FSTYPE}', '${MENDER_DATA_PART_FSTYPE}', d)}"

# Set the fstab options for mounting the data partition
MENDER_DATA_PART_FSTAB_OPTS ??= "${MENDER_DATA_PART_FSTAB_OPTS_DEFAULT}"
MENDER_DATA_PART_FSTAB_OPTS_DEFAULT = "defaults"

# Set any extra options for creating the data partition
MENDER_DATA_PART_FSOPTS ??= "${MENDER_DATA_PART_FSOPTS_DEFAULT}"
MENDER_DATA_PART_FSOPTS_DEFAULT = ""

# Filesystem type of boot partition, used for fstab construction.
# Typically the default (auto) will work fine
MENDER_BOOT_PART_FSTYPE ??= "${MENDER_BOOT_PART_FSTYPE_DEFAULT}"
MENDER_BOOT_PART_FSTYPE_DEFAULT = "auto"

# Set the fstab options for mounting the boot partition
MENDER_BOOT_PART_FSTAB_OPTS ??= "${MENDER_BOOT_PART_FSTAB_OPTS_DEFAULT}"
MENDER_BOOT_PART_FSTAB_OPTS_DEFAULT = "defaults,sync"

# Device type of device when making an initial partitioned image.
MENDER_DEVICE_TYPE ??= "${MENDER_DEVICE_TYPE_DEFAULT}"
MENDER_DEVICE_TYPE_DEFAULT = "${MACHINE}"

# To tell the difference from a beaglebone-yocto image with only U-Boot.
MENDER_DEVICE_TYPE_DEFAULT_beaglebone-yocto_mender-grub = "${MACHINE}-grub"

# Space separated list of device types compatible with the built update.
MENDER_DEVICE_TYPES_COMPATIBLE ??= "${MENDER_DEVICE_TYPES_COMPATIBLE_DEFAULT}"
MENDER_DEVICE_TYPES_COMPATIBLE_DEFAULT = "${MENDER_DEVICE_TYPE}"

# Total size of the medium that mender sdimg will be written to. The size of
# rootfs partition will be calculated automatically by subtracting the size of
# boot and data partitions along with some predefined overhead (see
# MENDER_PARTITIONING_OVERHEAD_KB).
MENDER_STORAGE_TOTAL_SIZE_MB ??= "${MENDER_STORAGE_TOTAL_SIZE_MB_DEFAULT}"
MENDER_STORAGE_TOTAL_SIZE_MB_DEFAULT ?= "1024"

# Size of the data partition, which is preserved across updates.
MENDER_DATA_PART_SIZE_MB ??= "${MENDER_DATA_PART_SIZE_MB_DEFAULT}"
MENDER_DATA_PART_SIZE_MB_DEFAULT = "128"

# Size of the swap partition, zero means not required
MENDER_SWAP_PART_SIZE_MB ??= "${MENDER_SWAP_PART_SIZE_MB_DEFAULT}"
MENDER_SWAP_PART_SIZE_MB_DEFAULT = "0"

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
#
# For traditional block storage (HDDs, SDDs, etc), in most cases this is 512
# bytes, often called a sector.
MENDER_STORAGE_PEB_SIZE ??= "8388608"

# Historically MENDER_PARTITION_ALIGNMENT was always in KiB, but due to UBI
# using some bytes for bookkeeping, each block is not always a KiB
# multiple. Hence it needs to be expressed in bytes in those cases.
MENDER_PARTITION_ALIGNMENT ??= "${MENDER_PARTITION_ALIGNMENT_DEFAULT}"
# For non-UBI, the alignment should simply be the physical erase block size,
# but it should not be less than 1KiB (wic won't like that).
MENDER_PARTITION_ALIGNMENT_DEFAULT = "${@max(${MENDER_STORAGE_PEB_SIZE}, 1024)}"

# The reserved space between the partition table and the first partition.
# Most people don't need to set this, and it will be automatically overridden
# by mender-uboot distro feature.
MENDER_RESERVED_SPACE_BOOTLOADER_DATA ??= "${MENDER_RESERVED_SPACE_BOOTLOADER_DATA_DEFAULT}"
MENDER_RESERVED_SPACE_BOOTLOADER_DATA_DEFAULT = "0"

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
MENDER_IMAGE_BOOTLOADER_FILE ??= "${MENDER_IMAGE_BOOTLOADER_FILE_DEFAULT}"
MENDER_IMAGE_BOOTLOADER_FILE_DEFAULT = ""

# Offset of bootloader, in sectors (512 bytes).
MENDER_IMAGE_BOOTLOADER_BOOTSECTOR_OFFSET ??= "${MENDER_IMAGE_BOOTLOADER_BOOTSECTOR_OFFSET_DEFAULT}"
MENDER_IMAGE_BOOTLOADER_BOOTSECTOR_OFFSET_DEFAULT = "2"

# File to flash into MBR (Master Boot Record) on partitioned images
MENDER_MBR_BOOTLOADER_FILE ??= "${MENDER_MBR_BOOTLOADER_FILE_DEFAULT}"
MENDER_MBR_BOOTLOADER_FILE_DEFAULT = ""
# How many bytes of the MBR to flash.
# 446 avoids the partition table structure. See this link:
# https://pete.akeo.ie/2014/05/compiling-and-installing-grub2-for.html
MENDER_MBR_BOOTLOADER_LENGTH ??= "446"

# Board specific U-Boot commands to be run prior to mender_setup
MENDER_UBOOT_PRE_SETUP_COMMANDS ??= "${MENDER_UBOOT_PRE_SETUP_COMMANDS_DEFAULT}"
MENDER_UBOOT_PRE_SETUP_COMMANDS_DEFAULT = ""

# Board specific U-Boot commands to be run after mender_setup
MENDER_UBOOT_POST_SETUP_COMMANDS ??= "${MENDER_UBOOT_POST_SETUP_COMMANDS_DEFAULT}"
MENDER_UBOOT_POST_SETUP_COMMANDS_DEFAULT = ""

# All the allowed mender configuration variables
MENDER_CONFIGURATION_VARS ?= "\
    RootfsPartA \
    RootfsPartB \
    InventoryPollIntervalSeconds \
    RetryPollIntervalSeconds \
    ArtifactVerifyKey \
    ServerCertificate \
    ServerURL \
    UpdatePollIntervalSeconds"

# The configuration variables to migrate to the persistent configuration.
MENDER_PERSISTENT_CONFIGURATION_VARS ?= "RootfsPartA RootfsPartB"


# --------------------------- END OF CONFIGURATION -----------------------------

IMAGE_INSTALL_append = " mender-client"
IMAGE_CLASSES += "mender-part-images mender-ubimg mender-artifactimg mender-dataimg mender-bootimg mender-datatar"

# Originally defined in bitbake.conf. We define them here so that images with
# the same MACHINE name, but different MENDER_DEVICE_TYPE, will not result in
# the same image file name.
IMAGE_NAME = "${IMAGE_BASENAME}-${MENDER_DEVICE_TYPE}${IMAGE_VERSION_SUFFIX}"
IMAGE_LINK_NAME = "${IMAGE_BASENAME}-${MENDER_DEVICE_TYPE}"

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

        # For GRUB, use BIOS for booting, instead of the default, UEFI.
        'mender-bios',

        # Integration with GRUB.
        'mender-grub',

        # Install of Mender, with the minimum components. This includes no
        # references to specific partition layouts.
        'mender-client-install',

        # Include components for Mender-partitioned images. This will create
        # files that rely on the Mender partition layout.
        'mender-image',

        # Include components for generating a BIOS GPT image.
        'mender-image-gpt',

        # Include components for generating a BIOS image.
        'mender-image-bios',

        # Include components for generating an SD image.
        'mender-image-sd',

        # Include components for generating a UBI image.
        'mender-image-ubi',

        # Include components for generating a UEFI image.
        'mender-image-uefi',

        # Include Mender as a systemd service.
        'mender-systemd',

        # Enable Mender configuration specific to UBI.
        'mender-ubi',

        # Use Mender together with U-Boot.
        'mender-uboot',

        # Use PARTUUID to set fixed drive locations.
        'mender-partuuid',

        # Setup the systemd machine ID to be persistent across OTA updates.
        'mender-persist-systemd-machine-id',

        # Enable dynamic resizing of the data filesystem through systemd's growfs
        'mender-growfs-data',
    }

    mfe = d.getVar('MENDER_FEATURES_ENABLE')
    mfe = mfe.split() if mfe is not None else []
    mfd = d.getVar('MENDER_FEATURES_DISABLE')
    mfd = mfd.split() if mfd is not None else []
    for feature in mfe + mfd:
        if not feature.startswith('mender-'):
            bb.fatal("%s in MENDER_FEATURES_ENABLE or MENDER_FEATURES_DISABLE is not a Mender feature."
                     % feature)

    for feature in d.getVar('DISTRO_FEATURES').split():
        if feature.startswith("mender-"):
            if feature not in mender_features:
                bb.fatal("%s from MENDER_FEATURES_ENABLE or DISTRO_FEATURES is not a valid Mender feature."
                         % feature)
            d.setVar('OVERRIDES_append', ':%s' % feature)

            # Verify that all 'mender-' features are added using MENDER_FEATURES
            # variables. This is important because we base some decisions on
            # these variables, and then fill DISTRO_FEATURES, which would give
            # infinite recursion if we based the decision directly on
            # DISTRO_FEATURES.
            if feature not in mfe or feature in mfd:
                bb.fatal(("%s is not added using MENDER_FEATURES_ENABLE and "
                          + "MENDER_FEATURES_DISABLE variables. Please make "
                          + "sure that the feature is enabled using "
                          + "MENDER_FEATURES_ENABLE, and is not in "
                          + "MENDER_FEATURES_DISABLE.")
                         % feature)
}

def mender_feature_is_enabled(feature, if_true, if_false, d):
    in_enable = bb.utils.contains('MENDER_FEATURES_ENABLE', feature, True, False, d)
    in_disable = bb.utils.contains('MENDER_FEATURES_DISABLE', feature, True, False, d)

    if in_enable and not in_disable:
        return if_true
    else:
        return if_false

python() {
    if d.getVar('MENDER_PARTITION_ALIGNMENT_MB', True):
        bb.fatal("MENDER_PARTITION_ALIGNMENT_MB is deprecated. Please define MENDER_PARTITION_ALIGNMENT instead.")
    if d.getVar('MENDER_PARTITION_ALIGNMENT_KB', True):
        bb.fatal("MENDER_PARTITION_ALIGNMENT_KB is deprecated. Please define MENDER_PARTITION_ALIGNMENT instead.")
    if d.getVar('MENDER_STORAGE_RESERVED_RAW_SPACE', True):
        bb.fatal("MENDER_STORAGE_RESERVED_RAW_SPACE is deprecated. Please define MENDER_RESERVED_SPACE_BOOTLOADER_DATA instead.")
    if d.getVar('IMAGE_BOOTLOADER_FILE', True):
        bb.fatal("IMAGE_BOOTLOADER_FILE is deprecated. Please define MENDER_IMAGE_BOOTLOADER_FILE instead.")
    if d.getVar('IMAGE_BOOTLOADER_BOOTSECTOR_OFFSET', True):
        bb.fatal("IMAGE_BOOTLOADER_BOOTSECTOR_OFFSET is deprecated. Please define MENDER_IMAGE_BOOTLOADER_BOOTSECTOR_OFFSET instead.")
    if d.getVar('MENDER_DATA_PART_DIR'):
        bb.fatal("MENDER_DATA_PART_DIR is deprecated. Please use recipes to add files directly to /data instead.")
}

addhandler mender_sanity_handler
mender_sanity_handler[eventmask] = "bb.event.ParseCompleted"
python mender_sanity_handler() {
    if bb.utils.contains('MENDER_FEATURES_ENABLE', 'mender-partuuid', True, False, d) and d.getVar('MENDER_STORAGE_DEVICE', True) != "":
        bb.warn("MENDER_STORAGE_DEVICE is ignored when mender-partuuid is enabled. Clear MENDER_STORAGE_DEVICE to remove this warning.")

    if bb.utils.contains('MENDER_FEATURES_ENABLE', 'mender-partuuid', True, False, d) and bb.utils.contains('MENDER_FEATURES_ENABLE', 'mender-uboot', True, False, d):
        bb.fatal("mender-partuuid is not supported with mender-uboot.")
}


def mender_get_bytes_with_unit(bytes):
    if bytes % 1048576 == 0:
        return "%dm" % (bytes / 1048576)
    if bytes % 1024 == 0:
        return "%dk" % (bytes / 1024)
    return "%d" % bytes


addhandler mender_vars_handler
mender_vars_handler[eventmask] = "bb.event.ParseCompleted"
python mender_vars_handler() {
    from bb import data
    import os
    import re
    import json

    path = d.getVar("LAYERDIR_MENDER")
    path = os.path.join(path, "conf/mender-vars.json")

    if os.path.isfile(path):
        mender_vars = {}
        with open(path, "r") as f:
            mender_vars = json.load(f)

        for k in d.keys():
            if k.startswith("MENDER_"):
                if re.search("_[-a-z0-9][-\w]*$", k) != None:
                    # skip variable overrides
                    continue;

                if k not in mender_vars.keys():
                    # Warn if user has defined some new (unused) MENDER_.* variables
                    bb.warn("\"%s\" is not a recognized MENDER_ variable. Typo?" % k)

                elif mender_vars[k] != "":
                    # If certain keys should have associated some restricted value
                    # (expressed in regular expression in the .json-file)
                    # NOTE: empty strings (json-values) are only compared by key, 
                    #       whereas the value is arbitrary
                    expected_expressions = []
                    val = d.getVar(k)

                    if isinstance (mender_vars[k], list):
                        # item is a list of strings
                        for regex in mender_vars[k]: # (can be a list of items)
                            if re.search(regex, val) == None:
                                expected_expressions += [regex]
                        if len(expected_expressions) > 0: 
                            bb.note("Variable \"%s\" does not contain suggested value(s): {%s}" %\
                                    (k, ', '.join(expected_expressions)))

                    else: 
                        # item is a single string
                        regex = mender_vars[k]
                        if re.search(regex, val) == None: 
                            bb.note("%s initialized with value \"%s\"" % (k, val),\
                                    " | Expected[regex]: \"%s\"" % regex)

    else: ## if !os.path.isfile(path): ##
        # This should never run, but left it in here in case we #
        # need to generate new json file template in the future #
        mender_vars = {}
        for k in d.keys():
            if k.startswith("MENDER_"):
                if re.search("_[-a-z0-9][-\w]*$", k) == None:
                    mender_vars[k] = ""
                    #mender_vars[k] = d.getVar(k) might be useful for inspection
        with open (path, 'w') as f:
            json.dump(mender_vars, f, sort_keys=True, indent=4)
}

# Including these does not mean that all these features will be enabled, just
# that their configuration will be considered. Use DISTRO_FEATURES to enable and
# disable features.
include mender-setup-bios.inc
include mender-setup-grub.inc
include mender-setup-image.inc
include mender-setup-install.inc
include mender-setup-systemd.inc
include mender-setup-ubi.inc
include mender-setup-uboot.inc
