inherit mender-install

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

# Size of the data partition, which is preserved across updates.
SDIMG_DATA_PART_SIZE_MB ?= "128"

# Size of the first (FAT) partition, that contains the bootloader
SDIMG_BOOT_PART_SIZE_MB ?= "128"

# For performance reasons, we try to align the partitions to the SD
# card's erase block. It is impossible to know this information with
# certainty, but one way to find out is to run the "flashbench" tool on
# your SD card and study the results. If you do, feel free to override
# this default.
#
# 8MB alignment is a safe setting that might waste some space if the
# erase block is smaller.
SDIMG_PARTITION_ALIGNMENT_MB ?= "8"

# u-boot environment file
IMAGE_UENV_TXT_FILE ?= "uEnv.txt"

# These are usually defined in the machine section, but for daisy this
# concept doesn't exist yet.
IMAGE_BOOT_FILES ?= "u-boot.${UBOOT_SUFFIX}"
IMAGE_BOOT_FILES_append_beaglebone = " MLO"
# This will be embedded into the boot sector, or close to the boot sector, where
# exactly depends on the offset variable.
IMAGE_BOOTLOADER_FILE ?= "u-boot.${UBOOT_SUFFIX}"
# Offset of bootloader, in sectors (512 bytes).
IMAGE_BOOTLOADER_BOOTSECTOR_OFFSET ?= "2"

########## CONFIGURATION END ##########

inherit image
inherit image_types

# We need to have the ext3 image generated already
IMAGE_TYPEDEP_sdimg = "ext3"

IMAGE_DEPENDS_sdimg = "util-linux-native dosfstools-native mtools-native e2fsprogs-native"

IMAGE_CMD_sdimg() {
    set -x

    mkdir -p "${WORKDIR}"

    # Workaround for the fact that the image builder requires this directory,
    # despite not using it. If "rm_work" is enabled, this directory won't always
    # exist.
    mkdir -p "${IMAGE_ROOTFS}"

    # Workaround for the fact the wic deletes its inputs (WTF??). These links
    # are disposable.
    ln -sfn "${DEPLOY_DIR_IMAGE}/${IMAGE_BASENAME}-${MACHINE}.ext3" \
        "${WORKDIR}/active.ext3"
    ln -sfn "${DEPLOY_DIR_IMAGE}/${IMAGE_BASENAME}-${MACHINE}.ext3" \
        "${WORKDIR}/inactive.ext3"

    dd if=/dev/zero of="${WORKDIR}/boot.vfat" count=0 bs=1M seek=${SDIMG_BOOT_PART_SIZE_MB}
    mkfs.vfat "${WORKDIR}/boot.vfat"

    # Copy uEnv.txt file to boot partition if file exists
    if [ -e ${DEPLOY_DIR_IMAGE}/${IMAGE_UENV_TXT_FILE} ] ; then
        mcopy -i "${WORKDIR}/boot.vfat" -v ${DEPLOY_DIR_IMAGE}/${IMAGE_UENV_TXT_FILE} ::
    fi

    # Copy boot files to boot partition
    for file in ${IMAGE_BOOT_FILES}
    do
        mcopy -i "${WORKDIR}/boot.vfat" -s ${DEPLOY_DIR_IMAGE}/$file ::
    done

    rm -rf "${WORKDIR}/data" || true
    if [ -n "${SDIMG_DATA_PART_DIR}" ]; then
        cp -a "${SDIMG_DATA_PART_DIR}" "${WORKDIR}/data"
    else
        mkdir -p "${WORKDIR}/data"
    fi

    # The OpenSSL certificates should go here:
    echo "dummy certificate" > "${WORKDIR}/data/mender.cert"

    SDIMG=${WORKDIR}/${IMAGE_BASENAME}-${MACHINE}.sdimg

    ALIGNMENT_SECTORS=$(expr ${SDIMG_PARTITION_ALIGNMENT_MB} \* 2048)
    ALIGNMENT_BYTES=$(expr $ALIGNMENT_SECTORS \* 512)

    # Boot partition sectors (primary)
    PART1_START_SECTORS=$ALIGNMENT_SECTORS
    PART1_SIZE_BYTES_UNALIGNED=$(stat -L -c %s ${WORKDIR}/boot.vfat)
    PART1_SIZE_BYTES=$(expr \( $PART1_SIZE_BYTES_UNALIGNED + $ALIGNMENT_BYTES - 1 \) / $ALIGNMENT_BYTES \* $ALIGNMENT_BYTES)
    PART1_END_SECTORS=$(expr $PART1_START_SECTORS + $PART1_SIZE_BYTES / 512 - 1)

    # Active partition sectors (primary)
    PART2_START_SECTORS=$(expr $PART1_END_SECTORS + 1)
    PART2_SIZE_BYTES_UNALIGNED=$(stat -L -c %s ${WORKDIR}/active.ext3)
    PART2_SIZE_BYTES=$(expr \( $PART2_SIZE_BYTES_UNALIGNED + $ALIGNMENT_BYTES - 1 \) / $ALIGNMENT_BYTES \* $ALIGNMENT_BYTES)
    PART2_END_SECTORS=$(expr $PART2_START_SECTORS + $PART2_SIZE_BYTES / 512 - 1)

    # Inactive partition sectors (primary)
    PART3_START_SECTORS=$(expr $PART2_END_SECTORS + 1)
    PART3_SIZE_BYTES_UNALIGNED=$(stat -L -c %s ${WORKDIR}/inactive.ext3)
    PART3_SIZE_BYTES=$(expr \( $PART3_SIZE_BYTES_UNALIGNED + $ALIGNMENT_BYTES - 1 \) / $ALIGNMENT_BYTES \* $ALIGNMENT_BYTES)
    PART3_END_SECTORS=$(expr $PART3_START_SECTORS + $PART3_SIZE_BYTES / 512 - 1)

    dd if=/dev/zero of=${WORKDIR}/data.ext3 count=0 bs=1M seek=${SDIMG_DATA_PART_SIZE_MB}
    mkfs.ext3 -F ${WORKDIR}/data.ext3 -d ${WORKDIR}/data

    # Extended partition sectors
    PART4_START_SECTORS=$(expr $PART3_END_SECTORS + 1)
    # One extra alignment block for extended partition table.
    PART4_SIZE_BYTES_UNALIGNED=$(expr $(stat -L -c %s ${WORKDIR}/data.ext3) + $ALIGNMENT_BYTES)
    PART4_SIZE_BYTES=$(expr \( $PART4_SIZE_BYTES_UNALIGNED + $ALIGNMENT_BYTES - 1 \) / $ALIGNMENT_BYTES \* $ALIGNMENT_BYTES)
    PART4_END_SECTORS=$(expr $PART4_START_SECTORS + $PART4_SIZE_BYTES / 512 - 1)

    # Data partition sectors (extended)
    # Starts inside the extended partition, after one alignment block.
    PART5_START_SECTORS=$(expr $PART4_START_SECTORS + $ALIGNMENT_SECTORS)
    PART5_SIZE_BYTES_UNALIGNED=$(stat -L -c %s ${WORKDIR}/data.ext3)
    PART5_SIZE_BYTES=$(expr \( $PART5_SIZE_BYTES_UNALIGNED + $ALIGNMENT_BYTES - 1 \) / $ALIGNMENT_BYTES \* $ALIGNMENT_BYTES)
    PART5_END_SECTORS=$(expr $PART5_START_SECTORS + $PART5_SIZE_BYTES / 512 - 1)

    # Sanity check: These should be equal.
    test $PART4_END_SECTORS -eq $PART5_END_SECTORS

    dd if=/dev/zero of=$SDIMG count=0 seek=$(expr $PART5_END_SECTORS + 1)
    (
        # Create DOS partition table
        echo o
        # 1st partition (FAT32)
        echo n
        echo p
        echo 1
        echo $PART1_START_SECTORS
        echo $PART1_END_SECTORS
        # 2nd partition (1st rootfs)
        echo n
        echo p
        echo 2
        echo $PART2_START_SECTORS
        echo $PART2_END_SECTORS
        # 3rd partition (2nd root)
        echo n
        echo p
        echo 3
        echo $PART3_START_SECTORS
        echo $PART3_END_SECTORS
        # 4th partition (extended)
        echo n
        echo e
        echo $PART4_START_SECTORS
        echo $PART4_END_SECTORS
        # 5th partition (data partition)
        echo n
        echo $PART5_START_SECTORS
        echo $PART5_END_SECTORS
        # 1st partition: bootable
        echo a
        echo 1
        # 1st partition: type W95 FAT16 (LBA)
        echo t
        echo 1
        echo e
        # 2nd partition: type Linux
        echo t
        echo 2
        echo 83
        # 3rd partition: type Linux
        echo t
        echo 3
        echo 83
        # 5th partition: type Linux
        echo t
        echo 5
        echo 83
        # COMMIT changes to image file
        echo p
        echo w

    ) | fdisk -c=nondos -u=sectors $SDIMG

    dd if=${WORKDIR}/boot.vfat of=$SDIMG seek=$PART1_START_SECTORS conv=notrunc
    dd if=${WORKDIR}/active.ext3 of=$SDIMG seek=$PART2_START_SECTORS conv=notrunc
    dd if=${WORKDIR}/inactive.ext3 of=$SDIMG seek=$PART3_START_SECTORS conv=notrunc
    dd if=${WORKDIR}/data.ext3 of=$SDIMG seek=$PART5_START_SECTORS conv=notrunc

    # Embed boot loader in image, offset relative to boot sector.
    if [ -n "${IMAGE_BOOTLOADER_FILE}" ]; then
        if [ $(expr ${SDIMG_PARTITION_ALIGNMENT_MB} \* 1048576 - ${IMAGE_BOOTLOADER_BOOTSECTOR_OFFSET} \* 512) -lt $(stat -c %s ${IMAGE_BOOTLOADER_FILE}) ]; then
            bberror "Not enough space to embed boot loader in boot sector. Increase SDIMG_PARTITION_ALIGNMENT_MB."
            exit 1
        fi

        dd if="${DEPLOY_DIR_IMAGE}/${IMAGE_BOOTLOADER_FILE}" of="$SDIMG" bs=512 seek=${IMAGE_BOOTLOADER_BOOTSECTOR_OFFSET} conv=notrunc
    fi

    mv "$SDIMG" "${DEPLOY_DIR_IMAGE}/${IMAGE_NAME}.sdimg"
    ln -sfn "${IMAGE_NAME}.sdimg" "${DEPLOY_DIR_IMAGE}/${IMAGE_BASENAME}-${MACHINE}.sdimg"
}
