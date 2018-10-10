## Default Mender variables
#
# MTD partitioning defined for colibri_imx7:
#
# #define MTDPARTS_DEFAULT	"mtdparts=gpmi-nand:"		\
# 				"512k(mx7-bcb),"		\
# 				"1536k(u-boot1)ro,"		\
# 				"1536k(u-boot2)ro,"		\
# 				"512k(u-boot-env),"		\
# 				"-(ubi)"

# 512MB of NAND flash
MENDER_STORAGE_TOTAL_SIZE_MB ?= "512"
# 512kB for iMX BCB, 2*1.5 MB for uboot and additional 512kB for uboot env, pretend it's a
# single boot partition
MENDER_BOOT_PART_SIZE_MB ?= "4"
# 16MB for data partition
MENDER_DATA_PART_SIZE_MB ?= "16"
# align to PEB size 128k
MENDER_PARTITION_ALIGNMENT_KB ?= "128"
# Account for UBI overhead, see
# http://www.linux-mtd.infradead.org/doc/ubi.html#L_overhead for details,
MENDER_STORAGE_RESERVED_RAW_SPACE ?= "20971520"
# all of above should give ~244MB for rootfs

# Since UBIFS employs compression (mkfs.ubifs -x lzo [default]), the total
# total rootfs size is hard to predict
# (see http://www.linux-mtd.infradead.org/misc.html). There also seems like
# there might be a bug in Yocto testing against the uncompressed rootfs size
# which in our case renders this check "useless", so we set IMAGE_ROOTFS_MAXSIZE
# to zero to skip this check.
IMAGE_ROOTFS_MAXSIZE ?= "0"

# NOTE: this affects only u-boot's autoconfigured headers, the same variable is
# also used for generating fw_env.config but because of assumptions made in
# meta-mender-core/recipes-bsp/u-boot/u-boot-fw-utils-mender.inc we need ship
# our own config instead.
MENDER_UBOOT_ENV_STORAGE_DEVICE_OFFSET ?= "0x380000"
# calculated offsets are:
# - 0x380000
# - 0x3c0000 (redundant env)

# make sure that kernel and devicetree are installed
MACHINE_ESSENTIAL_EXTRA_RDEPENDS += "kernel-image kernel-devicetree"
MACHINE_ESSENTIAL_EXTRA_RRECOMMENDS += "mtd-utils mtd-utils-ubifs"

# pick u-boot-toradex-fsl-fw-utils as provider of fw_{printenv,setenv}
PREFERRED_PROVIDER_u-boot-fw-utils ?= "u-boot-toradex-fsl-fw-utils"
PREFERRED_RPROVIDER_u-boot-fw-utils ?= "u-boot-toradex-fsl-fw-utils"

TORADEX_PRODUCT_IDS_colibri_imx7_append = " 0032 0033"

