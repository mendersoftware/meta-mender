EXTRA_IMAGEDEPENDS_append = "${@bb.utils.contains('DISTRO_FEATURES', 'mender-uboot', ' u-boot', '', d)}"


def mender_get_env_total_aligned_size(bootenv_size, alignment_bytes):
    env_aligned_size = int((bootenv_size + alignment_bytes - 1) / alignment_bytes) * alignment_bytes

    # Total size, original and redundant environment.
    total_env_size = env_aligned_size * 2

    return "%d" % total_env_size

MENDER_UBOOT_ENV_STORAGE_DEVICE_OFFSET ??= "${MENDER_PARTITION_ALIGNMENT}"

# The total occupied length of the environment on disk, after alignment has been
# taken into account. This is a guesstimate, and will be matched against the
# real size in the U-Boot recipe later. Must be an *even* multiple of the
# alignment. Most people should not need to set this, and if so, only because it
# produces an error if left to the default.
MENDER_RESERVED_SPACE_BOOTLOADER_DATA_DEFAULT_mender-uboot = \
    "${@mender_get_env_total_aligned_size(${MENDER_PARTITION_ALIGNMENT}, \
                                          ${MENDER_PARTITION_ALIGNMENT})}"

# make sure to provide a weak default
UBOOT_SUFFIX ??= "bin"
