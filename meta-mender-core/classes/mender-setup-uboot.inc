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

# Prefer to use our auto provided fw-utils variant which duplicates the sources
# from u-boot, so we don't have to apply the same patches twice.
PREFERRED_PROVIDER_u-boot-fw-utils ??= "${@mender_feature_is_enabled('mender-uboot', \
                                                                     'u-boot-fw-utils-mender-auto-provided', \
                                                                     '', \
                                                                     d)}"
PREFERRED_RPROVIDER_u-boot-fw-utils ??= "${@mender_feature_is_enabled('mender-uboot', \
                                                                      'u-boot-fw-utils-mender-auto-provided', \
                                                                      '', \
                                                                      d)}"

# This can be removed once u-boot-mender-tools is no longer needed.
PREFERRED_PROVIDER_u-boot-tools ??= "${@mender_feature_is_enabled('mender-uboot', \
                                                                  'u-boot-mender-tools', \
                                                                  'u-boot-tools', \
                                                                  d)}"
PREFERRED_RPROVIDER_nativesdk-u-boot-mkimage ??= "${@mender_feature_is_enabled('mender-uboot', \
                                                                               'nativesdk-u-boot-mender-tools', \
                                                                               'nativesdk-u-boot-tools', \
                                                                               d)}"
