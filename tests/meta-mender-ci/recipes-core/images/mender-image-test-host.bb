require recipes-extended/images/core-image-full-cmdline.bb

DESCRIPTION = "Mender CI - test environment host system image"

IMAGE_FEATURES_remove = "splash"

IMAGE_FEATURES_append = " \
                      debug-tweaks \
                      package-management \
                      "

# need SSH client
IMAGE_INSTALL += "openssh-ssh"

# rsync may be useful too
IMAGE_INSTALL += "rsync"

# we'll likely need to do some work with partitions and filesystems
IMAGE_INSTALL += "\
              parted \
              e2fsprogs \
              e2fsprogs-mke2fs e2fsprogs-e2fsck \
              mtd-utils \
              mtd-utils-ubifs \
              "
# we may need to access/modify u-boot environment
IMAGE_INSTALL += "u-boot-fw-utils"

# we don't really need mender nor mender-artifact-info
IMAGE_INSTALL_remove = "mender mender-artifact-info"

# install QA tools
IMAGE_INSTALL += "mender-qa"
