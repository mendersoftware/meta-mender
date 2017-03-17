# Class for those who want a Mender-enabled U-Boot.

inherit mender-install

# ------------------------------ CONFIGURATION ---------------------------------

# The interface to load partitions from. This is normally empty, in which case
# it is deduced from MENDER_STORAGE_DEVICE. Only use this if the interface
# cannot be deduced from MENDER_STORAGE_DEVICE.
MENDER_UBOOT_STORAGE_INTERFACE ??= ""

# The device number of the interface to load partitions from. This is normally
# empty, in which case it is deduced from MENDER_STORAGE_DEVICE. Only use this
# if the indexing of devices is different in U-Boot and in the Linux kernel.
MENDER_UBOOT_STORAGE_DEVICE ??= ""

# --------------------------- END OF CONFIGURATION -----------------------------

EXTRA_IMAGEDEPENDS += "u-boot"
PACKAGECONFIG_append_pn-mender = " u-boot"

def mender_kb2bytes(kb):
    return kb * 1024

def mender_get_env_total_aligned_size(bootenv_size, alignment_kb):
    alignment_bytes = alignment_kb * 1024
    env_aligned_size = int((bootenv_size + alignment_bytes - 1) / alignment_bytes) * alignment_bytes

    # Total size, original and redundant environment.
    total_env_size = env_aligned_size * 2

    return "%d" % total_env_size

MENDER_UBOOT_ENV_STORAGE_DEVICE_OFFSET ?= "${@mender_kb2bytes(${MENDER_PARTITION_ALIGNMENT_KB})}"

# The total occupied length of the environment on disk, after alignment has been
# taken into account. This is a guesstimate, and will be matched against the
# real size in the U-Boot recipe later. Must be an *even* multiple of the
# alignment. Most people should not need to set this, and if so, only because it
# produces an error if left to the default.
MENDER_STORAGE_RESERVED_RAW_SPACE ?= "${@mender_get_env_total_aligned_size(${MENDER_PARTITION_ALIGNMENT_KB}, ${MENDER_PARTITION_ALIGNMENT_KB})}"
