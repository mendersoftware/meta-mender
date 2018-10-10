# We provide our custom fw_env.config and that is why we include
# u-boot-mender-common instead of u-boot-fw-utils-mender
require recipes-bsp/u-boot/u-boot-mender-common.inc
require u-boot-mender-toradex-nxp.inc
