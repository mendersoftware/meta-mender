EXTRA_IMAGEDEPENDS_append = "${@bb.utils.contains('DISTRO_FEATURES', 'mender-uboot', ' u-boot', '', d)}"


def mender_get_env_total_aligned_size(bootenv_size, bootenv_range, alignment_kb):
    alignment_bytes = alignment_kb * 1024

    if bootenv_range and type(bootenv_range) is str:
        base = 16 if bootenv_range.startswith('0x') else 10
        bootenv_range = int(bootenv_range, base)
    else:
        bootenv_range = 0

    if bootenv_range > 0:
        if bootenv_range < bootenv_size:
           raise Exception('BOOTENV_RANGE (0x{:x}) is smaller than ' \
                           'BOOTENV_SIZE (0x{:x})'.format(bootenv_range,
                                                          bootenv_size))
        # override bootenv size for further calculations
        bootenv_size = bootenv_range

    env_aligned_size = int((bootenv_size + alignment_bytes - 1) / alignment_bytes) * alignment_bytes

    # Total size, original and redundant environment.
    total_env_size = env_aligned_size * 2

    return "%d" % total_env_size

MENDER_UBOOT_ENV_STORAGE_DEVICE_OFFSET ??= "${@eval('${MENDER_PARTITION_ALIGNMENT_KB} * 1024')}"

# The total occupied length of the environment on disk, after alignment has been
# taken into account. This is a guesstimate, and will be matched against the
# real size in the U-Boot recipe later. Must be an *even* multiple of the
# alignment. Most people should not need to set this, and if so, only because it
# produces an error if left to the default.
MENDER_STORAGE_RESERVED_RAW_SPACE_DEFAULT_mender-uboot = \
    "${@mender_get_env_total_aligned_size(${MENDER_PARTITION_ALIGNMENT_KB}, \
                                          ${MENDER_PARTITION_ALIGNMENT_KB}, \
                                          ${MENDER_PARTITION_ALIGNMENT_KB})}"

# make sure to provide a weak default
UBOOT_SUFFIX ??= "bin"

# Prefer to use our auto provided fw-utils variant which duplicates the sources
# from u-boot, so we don't have to apply the same patches twice.
PREFERRED_PROVIDER_u-boot-fw-utils ??= "u-boot-fw-utils-mender-auto-provided"
PREFERRED_RPROVIDER_u-boot-fw-utils ??= "u-boot-fw-utils-mender-auto-provided"
