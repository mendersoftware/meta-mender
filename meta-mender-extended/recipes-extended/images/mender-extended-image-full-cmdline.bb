require recipes-extended/images/core-image-full-cmdline.bb

# Docker and containers need more storage space
MENDER_STORAGE_TOTAL_SIZE_MB ?= "2048"
MENDER_DATA_PART_SIZE_MB ?= "512"

IMAGE_INSTALL:append = " mender-docker-compose"
