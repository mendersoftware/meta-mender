require recipes-extended/images/core-image-full-cmdline.bb

IMAGE_FEATURES += "ssh-server-openssh allow-empty-password debug-tweaks"
IMAGE_INSTALL_append = " mender-configure"

IMAGE_LINK_NAME = "${IMAGE_BASENAME}-${MENDER_DEVICE_TYPE}-${MENDER_ARTIFACT_NAME}"  
