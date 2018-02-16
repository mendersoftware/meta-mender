################################################################################
# Variables
################################################################################

ARTIFACTIMG_FSTYPE_DEFAULT_mender-ubi = "ubifs"

MENDER_STORAGE_DEVICE_DEFAULT_mender-ubi = "ubi0"

# The base name of the devices that hold individual volumes.
MENDER_STORAGE_DEVICE_BASE_DEFAULT_mender-ubi = "${MENDER_STORAGE_DEVICE}_"

# The numbers of the two rootfs partitions in the A/B partition layout.
MENDER_ROOTFS_PART_A_DEFAULT_mender-ubi = "${MENDER_STORAGE_DEVICE_BASE}0"
MENDER_ROOTFS_PART_B_DEFAULT_mender-ubi = "${MENDER_STORAGE_DEVICE_BASE}1"

# The partition number holding the data partition.
MENDER_DATA_PART_DEFAULT_mender-ubi = "${MENDER_STORAGE_DEVICE_BASE}2"
MENDER_DATA_PART_FSTYPE_DEFAULT_mender-ubi = "ubifs"

# u-boot command ubifsmount requires volume name as the only argument
# and hence we need to keep track of that since we load kernel/dtb from
# rootfs part
#
# It also needs the volume index e.g.
# ubifsmount ubi0:rootfsa
MENDER_ROOTFS_PART_A_NAME_DEFAULT_mender-ubi = "${MENDER_STORAGE_DEVICE}:rootfsa"
MENDER_ROOTFS_PART_B_NAME_DEFAULT_mender-ubi = "${MENDER_STORAGE_DEVICE}:rootfsb"

# The name of of the MTD part holding your UBI volumes.
MENDER_MTD_UBI_DEVICE_NAME_DEFAULT_mender-ubi = "ubi"

# Boot part is not used when building UBI image.
MENDER_BOOT_PART_DEFAULT_mender-ubi = ""
MENDER_BOOT_PART_SIZE_MB_DEFAULT_mender-ubi = "0"

# These are not applicable when building UBI image.
MENDER_UBOOT_STORAGE_DEVICE_DEFAULT_mender-ubi = "dummy"
MENDER_UBOOT_STORAGE_INTERFACE_DEFAULT_mender-ubi = "dummy"

MENDER_PARTITION_ALIGNMENT_KB_DEFAULT_mender-ubi = "1024"

# Will be relative to start of first MTD partition, so should be zero.
IMAGE_BOOTLOADER_BOOTSECTOR_OFFSET_DEFAULT_mender-ubi = "0"

# since UBIFS employs compression, disable the max rootfs size checking.
MENDER_IMAGE_ROOTFS_MAXSIZE_DEFAULT_mender-ubi = ""

# Definition of mtdids and mtdparts (taken from U-Boot's mtdparts.c):
#
# 'mtdids' - linux kernel mtd device id <-> u-boot device id mapping
#
# mtdids=<idmap>[,<idmap>,...]
#
# <idmap>    := <dev-id>=<mtd-id>
# <dev-id>   := 'nand'|'nor'|'onenand'<dev-num>
# <dev-num>  := mtd device number, 0...
# <mtd-id>   := unique device tag used by linux kernel to find mtd device (mtd->name)
#
#
# 'mtdparts' - partition list
#
# mtdparts=mtdparts=<mtd-def>[;<mtd-def>...]
#
# <mtd-def>  := <mtd-id>:<part-def>[,<part-def>...]
# <mtd-id>   := unique device tag used by linux kernel to find mtd device (mtd->name)
# <part-def> := <size>[@<offset>][<name>][<ro-flag>]
# <size>     := standard linux memsize OR '-' to denote all remaining space
# <offset>   := partition start offset within the device
# <name>     := '(' NAME ')'
# <ro-flag>  := when set to 'ro' makes partition read-only (not used, passed to kernel)
#
# Notes:
# - each <mtd-id> used in mtdparts must albo exist in 'mtddis' mapping
# - if the above variables are not set defaults for a given target are used
#
# Examples:
#
# 1 NOR Flash, with 1 single writable partition:
# mtdids=nor0=edb7312-nor
# mtdparts=mtdparts=edb7312-nor:-
#
# 1 NOR Flash with 2 partitions, 1 NAND with one
# mtdids=nor0=edb7312-nor,nand0=edb7312-nand
# mtdparts=mtdparts=edb7312-nor:256k(ARMboot)ro,-(root);edb7312-nand:-(home)

# The mtdids present on the device.
# Highly board specific, therefore there is no default.
MENDER_MTDIDS ??= ""

# If there is more than one mtdid, the mtdid that contains Mender.
# This should be the one after the equals sign in MENDER_MTDIDS.
# Currently there is no support for spreading over more than one.
MENDER_IS_ON_MTDID ??= "${@mender_default_mender_mtdid('${MENDER_MTDIDS}')}"

# The mtdparts string for the MTD layout. Usually auto-set from MENDER_MTDIDS
# if possible.
MENDER_MTDPARTS ??= "${@mender_make_mtdparts(d)}"

# Usually included in first mtd partition.
MENDER_IMAGE_BOOTLOADER_FILE_DEFAULT_mender-ubi = "u-boot.${UBOOT_SUFFIX}"


################################################################################
# Functions
################################################################################

def mender_default_mender_mtdid(mtdids):
    if len(mtdids.split(",")) == 1 and len(mtdids.split("=")) == 2:
        return mtdids.split("=")[1]
    else:
        # We don't know what to pick, choose nothing.
        return ""

def mender_make_mtdparts(d):
    if not bb.utils.contains('DISTRO_FEATURES', 'mender-ubi', True, False, d):
        return ""

    mtdids = d.getVar('MENDER_MTDIDS')
    if not mtdids or len(mtdids.split(",")) > 1:
        return ""

    active_mtdid = d.getVar('MENDER_IS_ON_MTDID')
    if not active_mtdid:
        return ""

    alignment = int(d.getVar('MENDER_PARTITION_ALIGNMENT_KB')) * 1024

    bootloader = ""
    if bb.utils.contains('DISTRO_FEATURES', 'mender-uboot', True, False, d):
        bootloader = "%s(u-boot)ro,%s(u-boot-env)," % (mender_get_bytes_with_unit(alignment),
                                                       mender_get_bytes_with_unit(alignment * 2))

    return "%s:%s-(ubi)" % (active_mtdid, bootloader)

mender_get_mtdparts() {
    if [ -n "${MENDER_MTDPARTS}" ]; then
        echo "${MENDER_MTDPARTS}"
    else
        local mtdparts="${@mender_make_mtdparts(d)}"
        if [ -n "$mtdparts" ]; then
            echo "$mtdparts"
        else
            bbwarn "Unable to generate mtdparts. Make sure that MENDER_MTDIDS contains only one assignment, or, if this is not possible, set MENDER_IS_ON_MTDID and MENDER_MTDPARTS manually."
        fi
    fi
}
