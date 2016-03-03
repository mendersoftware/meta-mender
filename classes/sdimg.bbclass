# Class that creates an SD card image that boots under qemu's emulation
# for vexpress-a9 board. See the script mender-qemu for an example of
# how to boot the image.

# The partitioning scheme is:
#    part1: FAT partition with bootloader
#    part2: first rootfs, active
#    part3: second rootfs, inactive, mirror of first,
#           available as failsafe for when some update fails
#    part4: extended partition
#    part5: persistent data partition


########## CONFIGURATION START - you can override these default
##########                       values in your local.conf


# Optional location where a directory can be specified with content that should
# be included on the data partition. Some of Mender's own files will be added to
# this (e.g. OpenSSL certificates).
SDIMG_DATA_PART_DIR ?= ""

# Size of the first (FAT) partition, that contains the bootloader
SDIMG_PART1_SIZE_MB ?= "128"

# For performance reasons, we try to align the partitions to the SD
# card's erase block. It is impossible to know this information with
# certainty, but one way to find out is to run the "flashbench" tool on
# your SD card and study the results. If you do, feel free to override
# this default.
#
# 8MB alignment is a safe setting that might waste some space if the
# erase block is smaller.
SDIMG_PARTITION_ALIGNMENT_MB ?= "8"

# u-boot environment file to be stored on boot partition
IMAGE_BOOT_ENV_FILE ?= "uboot.env"

# u-boot environment file
IMAGE_UENV_TXT_FILE ?= "uEnv.txt"

########## CONFIGURATION END ##########

inherit image_types

WKS_FULL_PATH = "${WORKDIR}/mender-sdimg.wks"

# We need to have the ext3 image generated already
IMAGE_TYPEDEP_sdimg = "ext3"

IMAGE_DEPENDS_sdimg = "${IMAGE_DEPENDS_wic} dosfstools"

IMAGE_CMD_sdimg() {
    mkdir -p "${WORKDIR}"

    # Workaround for the fact that the image builder requires this directory,
    # despite not using it. If "rm_work" is enabled, this directory won't always
    # exist.
    mkdir -p "${IMAGE_ROOTFS}"

    # Workaround for the fact the wic deletes its inputs (WTF??). These links
    # are disposable.
    ln -sfn "${DEPLOY_DIR_IMAGE}/${IMAGE_BASENAME}-${MACHINE}.ext3" \
        "${WORKDIR}/part1.tmp"
    ln -sfn "${DEPLOY_DIR_IMAGE}/${IMAGE_BASENAME}-${MACHINE}.ext3" \
        "${WORKDIR}/part2.tmp"

    PART1_SIZE=$(expr ${SDIMG_PART1_SIZE_MB} \* 2048)
    SDIMG_PARTITION_ALIGNMENT_KB=$(expr ${SDIMG_PARTITION_ALIGNMENT_MB} \* 1024)

    dd if=/dev/zero of="${WORKDIR}/fat.dat" count=${PART1_SIZE}
    mkfs.vfat "${WORKDIR}/fat.dat"

    # Create empty environment. Just so that the file is available.
    dd if=/dev/zero of="${WORKDIR}/${IMAGE_BOOT_ENV_FILE}" count=0 bs=1K seek=256
    mcopy -i "${WORKDIR}/fat.dat" -v ${WORKDIR}/${IMAGE_BOOT_ENV_FILE} ::
    rm -f "${WORKDIR}/${IMAGE_BOOT_ENV_FILE}"

    # Copy uEnv.txt file to boot partition if file exists
    if [ -e ${DEPLOY_DIR_IMAGE}/${IMAGE_UENV_TXT_FILE} ] ; then
        mcopy -i "${WORKDIR}/fat.dat" -v ${DEPLOY_DIR_IMAGE}/${IMAGE_UENV_TXT_FILE} ::
    fi

    # Copy boot files to boot partition
    mcopy -i "${WORKDIR}/fat.dat" -s ${DEPLOY_DIR_IMAGE}/${IMAGE_BOOT_FILES} ::

    rmdir "${WORKDIR}/data" || true
    if [ -n "${SDIMG_DATA_PART_DIR}" ]; then
        cp -a "${SDIMG_DATA_PART_DIR}" "${WORKDIR}/data"
    else
        mkdir -p "${WORKDIR}/data"
    fi

    # The OpenSSL certificates should go here:
    echo "dummy certificate" > "${WORKDIR}/data/mender.cert"

    cat > "${WORKDIR}/mender-sdimg.wks" <<EOF
part /u-boot --source fsimage --sourceparams=file="${WORKDIR}/fat.dat"  --ondisk mmcblk0 --fstype=vfat --label boot --active  --align $SDIMG_PARTITION_ALIGNMENT_KB
part /       --source fsimage --sourceparams=file="${WORKDIR}/part1.tmp" --ondisk mmcblk0 --fstype=ext3 --label platform --align $SDIMG_PARTITION_ALIGNMENT_KB
part /       --source fsimage --sourceparams=file="${WORKDIR}/part2.tmp" --ondisk mmcblk0 --fstype=ext3 --label platform --align $SDIMG_PARTITION_ALIGNMENT_KB
part /data   --source rootfs  --rootfs-dir="${WORKDIR}/data"             --ondisk mmcblk0 --fstype=ext3 --label data     --align $SDIMG_PARTITION_ALIGNMENT_KB

# Note: "bootloader" appears to be useless in this context, but the wic
# framework requires that it be present.
bootloader --timeout=10  --append=""
EOF

    # Call WIC
    IMAGE_CMD_wic

    mv "${DEPLOY_DIR_IMAGE}/${IMAGE_NAME}.rootfs.wic" "${DEPLOY_DIR_IMAGE}/${IMAGE_NAME}.sdimg"
    ln -sfn "${IMAGE_NAME}.sdimg" "${DEPLOY_DIR_IMAGE}/${IMAGE_BASENAME}-${MACHINE}.sdimg"
}
