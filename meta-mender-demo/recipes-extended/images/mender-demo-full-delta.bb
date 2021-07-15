require recipes-extended/images/mender-demo-full-rw.bb

IMAGE_FEATURES_append = " read-only-rootfs"
IMAGE_INSTALL_append = " mender-binary-delta"

# See https://tracker.mender.io/browse/MEN-3513 and
# https://tracker.mender.io/browse/MEN-3781 and
# https://tracker.mender.io/browse/MEN-3912.
EXTRA_IMAGECMD_ext4_append = "${@bb.utils.contains('IMAGE_FEATURES', 'read-only-rootfs', ' -O ^64bit -O ^has_journal', '', d)}"
