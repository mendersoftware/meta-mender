# Estimate how much space may be lost due to partitioning alignment. Use a
# simple heuristic for now - 4 partitions * alignment
def mender_get_part_overhead(d):
    align = d.getVar('MENDER_PARTITION_ALIGNMENT_KB', True)
    if align:
        return 4 * int(align)
    return 0

# Overhead lost due to partitioning.
MENDER_PARTITIONING_OVERHEAD_KB ?= "${@mender_get_part_overhead(d)}"

def mender_calculate_rootfs_size_kb(total_mb, boot_mb, data_mb, overhead_kb, reserved_space_size):
    # Space left in raw device.
    calc_space = (total_mb - boot_mb - data_mb) * 1048576 - overhead_kb * 1024

    # Subtract reserved raw space.
    calc_space = calc_space - reserved_space_size

    # Split in two.
    calc_space = calc_space / 2

    # Turn into kiB.
    calc_space_kb = calc_space / 1024

    return int(calc_space_kb)

# Auto detect image size from other settings.
MENDER_CALC_ROOTFS_SIZE = "${@mender_calculate_rootfs_size_kb(${MENDER_STORAGE_TOTAL_SIZE_MB}, \
                                                              ${MENDER_BOOT_PART_SIZE_MB}, \
                                                              ${MENDER_DATA_PART_SIZE_MB}, \
                                                              ${MENDER_PARTITIONING_OVERHEAD_KB}, \
                                                              ${MENDER_STORAGE_RESERVED_RAW_SPACE})}"

# Gently apply this as the default image size.
# But subtract IMAGE_ROOTFS_EXTRA_SPACE, since it will be added automatically
# in later bitbake calculations.
IMAGE_ROOTFS_SIZE ?= "${@eval('${MENDER_CALC_ROOTFS_SIZE} - (${IMAGE_ROOTFS_EXTRA_SPACE})')}"

# Set hard limit on maximum rootfs size. Calculated rootfs size is used when
# partitioning the disk image (be it SD card or UBI image), and defines an upper
# bound of the space allocated for rootfs partition/volume.
IMAGE_ROOTFS_MAXSIZE ?= "${MENDER_CALC_ROOTFS_SIZE}"
