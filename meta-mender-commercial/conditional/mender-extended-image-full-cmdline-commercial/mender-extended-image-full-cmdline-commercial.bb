require recipes-extended/images/mender-extended-image-full-cmdline.bb

IMAGE_INSTALL:append = " mender-delta-docker-compose"
