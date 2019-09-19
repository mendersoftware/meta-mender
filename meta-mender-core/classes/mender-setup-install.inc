# Estimate how much space may be lost due partition table. This is based on the
# assumption that GPT uses one set of sectors at the start of the disk, and one
# at the end. This wastes a little bit of space in the non-GPT case, which only
# puts data at the start.
def mender_get_part_overhead_kb(d):
    import math

    align = int(d.getVar('MENDER_PARTITION_ALIGNMENT'))
    if align:
        return 2 * int(math.ceil(align / 1024))
    return 0

# Overhead lost due to partitioning.
MENDER_PARTITIONING_OVERHEAD_KB ??= "${MENDER_PARTITIONING_OVERHEAD_KB_DEFAULT}"
MENDER_PARTITIONING_OVERHEAD_KB_DEFAULT = "${@mender_get_part_overhead_kb(d)}"

def mender_calculate_rootfs_size_kb(total_mb, boot_mb, data_mb, swap_mb, alignment, overhead_kb, reserved_space_size):
    import math

    # Space used by each of the partitions, aligned to partition alignment
    calc_space = math.ceil(boot_mb * 1048576 / alignment) * alignment
    calc_space += math.ceil(data_mb * 1048576 / alignment) * alignment
    calc_space += math.ceil(swap_mb * 1048576 / alignment) * alignment

    # Remaining space after partitions and overhead are subtracted.
    calc_space = total_mb * 1048576 - calc_space - overhead_kb * 1024

    # Subtract reserved raw space.
    calc_space = calc_space - reserved_space_size

    # Split in two.
    calc_space = calc_space / 2

    # Need to align to partition alignment, and round down.
    calc_space = int(calc_space / alignment) * alignment

    # Turn into kiB.
    calc_space_kb = calc_space / 1024

    return int(calc_space_kb)

# Auto detect image size from other settings.
MENDER_CALC_ROOTFS_SIZE = "${@mender_calculate_rootfs_size_kb(${MENDER_STORAGE_TOTAL_SIZE_MB}, \
                                                              ${MENDER_BOOT_PART_SIZE_MB}, \
                                                              ${MENDER_DATA_PART_SIZE_MB}, \
                                                              ${MENDER_SWAP_PART_SIZE_MB}, \
                                                              ${MENDER_PARTITION_ALIGNMENT}, \
                                                              ${MENDER_PARTITIONING_OVERHEAD_KB}, \
                                                              ${MENDER_RESERVED_SPACE_BOOTLOADER_DATA})}"

# Gently apply this as the default image size.
# But subtract IMAGE_ROOTFS_EXTRA_SPACE, since it will be added automatically
# in later bitbake calculations.
IMAGE_ROOTFS_SIZE ?= "${MENDER_IMAGE_ROOTFS_SIZE_DEFAULT}"
MENDER_IMAGE_ROOTFS_SIZE_DEFAULT ?= "${@eval('${MENDER_CALC_ROOTFS_SIZE} - (${IMAGE_ROOTFS_EXTRA_SPACE})')}"

# Disable rootfs upper bound checking by setting a large default value (100GB)
#
# This is primarily done because of the mender-dataimg.bbclass, which is an
# image that is created from a sub-directory in the rootfs tree and this size
# check is not applicable in this case (generates false negatives)
#
# We have custom sanity checks of image sizes that ensures that the generated
# filesystem images fit in to the defined partition sizes of the disk image.
IMAGE_ROOTFS_MAXSIZE_forcevariable = "102400000"
