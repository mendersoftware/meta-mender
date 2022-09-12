require recipes-extended/images/core-image-full-cmdline.bb

IMAGE_FEATURES:append = " read-only-rootfs"

# See https://tracker.mender.io/browse/MEN-3513 and
# https://tracker.mender.io/browse/MEN-3781 and
# https://tracker.mender.io/browse/MEN-3912.
EXTRA_IMAGECMD:ext4:append = "${@bb.utils.contains('IMAGE_FEATURES', 'read-only-rootfs', ' -O ^64bit -O ^has_journal', '', d)}"
