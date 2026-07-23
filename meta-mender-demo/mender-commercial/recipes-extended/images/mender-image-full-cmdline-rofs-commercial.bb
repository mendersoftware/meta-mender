require recipes-extended/images/mender-image-full-cmdline-rofs.bb

IMAGE_INSTALL:append = " mender-binary-delta"
