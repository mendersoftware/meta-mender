FILESEXTRAPATHS_prepend := "${THISDIR}/files:"

MENDER_UBOOT_AUTO_CONFIGURE = "0"

# toradex board is using 2016.11 u-boot, need to apply a patch that matches our version
SRC_URI_remove = "file://0003-Integration-of-Mender-boot-code-into-U-Boot.patch"
SRC_URI_append = " file://0003-U-Boot-pre-2017.03-integration-of-Mender-boot-code-i.patch"

# 128kB
BOOTENV_SIZE_vf ?= "0x20000"

SRC_URI_append_vf = " file://0001-configs-colibri_vf-adjust-for-Mender-requirements.patch"
SRC_URI_append_vf = " file://0002-configs-colibri_vf-increase-SYS_MALLOC_LEN-to-8-MB.patch"
SRC_URI_append_vf = " file://0003-colibri_vf-disable-FIT-image-enable-UBIFS.patch"

# 128kB
BOOTENV_SIZE_colibri-imx7 ?= "0x20000"

SRC_URI_append_colibri-imx7 = " file://0001-colibri-imx7-mender-integration-primer-enable-BOOTCO.patch"
SRC_URI_append_colibri-imx7 = " file://0002-colibri-imx7-set-CONFIG_ENV_RANGE-to-cover-2-environ.patch"
SRC_URI_append_colibri-imx7 = " file://0003-colibri-imx7-mender-integration-override-ubiboot-and.patch"
