require recipes-extended/images/core-image-full-cmdline.bb

IMAGE_FEATURES:append += " read-only-rootfs"

IMAGE_INSTALL:append = " mender-binary-delta"
