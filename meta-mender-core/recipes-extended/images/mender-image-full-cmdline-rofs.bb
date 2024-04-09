require recipes-extended/images/core-image-full-cmdline.bb

IMAGE_FEATURES_append = " read-only-rootfs"
