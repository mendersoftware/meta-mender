# Class that creates an SD card image that boots under qemu's emulation
# for vexpress-a9 board. See the script mender-qemu for an example of
# how to boot the image.

# The partitioning scheme is:
#    part1: FAT partition with bootloader
#    part2: first rootfs, active
#    part3: second rootfs, inactive, mirror of first,
#           available as failsafe for when some update fails


########## CONFIGURATION START - you can override these default
##########                       values in your local.conf


# Total size of the SD card. The two rootfs partition sizes are
# auto-determined to fill the space of the SD card.
SDIMG_SIZE_MB ?= "1000"

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


########## CONFIGURATION END ##########


# This script depends on:
#     util-linux (fdisk)
#     dosfstools (mkfs.vfat)
#     mtools     (mcopy)
#     e2fsprogs  (resize2fs)
IMAGE_DEPENDS_sdimg = "util-linux-native dosfstools-native mtools-native e2fsprogs-native"

# We need to have the ext3 image generated already
IMAGE_TYPEDEP_sdimg = "ext3"

IMAGE_BOOT_ENV_FILE ?= "uboot.env"


IMAGE_CMD_sdimg () {

    set -x                                      # debug output
    set -e                                      # exit on error
    set -u                                      # exit on unset variable
    # Needs bash, TODO can I require that this runs under bash?
    # set -o pipefail                             # don't hide pipeline errors

    cd ${DEPLOY_DIR_IMAGE}
    ROOTFS_IMG=${IMAGE_NAME}.rootfs.ext3
    SDIMG=${IMAGE_NAME}.rootfs.sdimg

    # Assert rootfs has been correctly generated
    test -e ${ROOTFS_IMG}

    # Compute partition borders and sizes, EVERYTHING IN SECTORS (512 bytes)

    SDIMG_SIZE_SECTORS=$(expr ${SDIMG_SIZE_MB} \* 2048)
    PART1_SIZE=$(expr ${SDIMG_PART1_SIZE_MB} \* 2048)

    ALIGNMENT=$(expr ${SDIMG_PARTITION_ALIGNMENT_MB} \* 2048)
    PART1_START=${ALIGNMENT}
    PART1_END=$(expr ${PART1_START} + ${PART1_SIZE} - 1)
    PART2_START=$(expr \( 1 + ${PART1_END} / ${ALIGNMENT} \) \* ${ALIGNMENT})
    PART23_SIZE_UNALIGNED=$(expr \( ${SDIMG_SIZE_SECTORS} - ${PART2_START} \) / 2)
    PART23_SIZE=$(expr ${PART23_SIZE_UNALIGNED} - ${PART23_SIZE_UNALIGNED} % ${ALIGNMENT})
    PART2_END=$(expr ${PART2_START} + ${PART23_SIZE} - 1)
    PART3_START=$(expr \( 1 + ${PART2_END} / ${ALIGNMENT} \) \* ${ALIGNMENT})
    PART3_END=$(expr ${PART3_START} + ${PART23_SIZE} - 1)

    # Assert we are not past the limits of the SD card size
    test ${PART3_END} -lt ${SDIMG_SIZE_SECTORS}

    # Resize rootfs to be as big as the partitions 2 and 3
    resize2fs ${ROOTFS_IMG} ${PART23_SIZE}s

    # Assert that the rootfs size is smaller than PART23_SIZE
    ROOTFS_SIZE=$(wc -c ${ROOTFS_IMG} | cut -d\  -f1 )
    test ${ROOTFS_SIZE} -le $(expr ${PART23_SIZE} \* 512)

    dd if=/dev/zero of=${SDIMG} count=0 seek=${SDIMG_SIZE_SECTORS}
    export PART1_START PART1_END PART2_START PART2_END PART3_START PART3_END
    (
        # Create DOS partition table
        echo o
        # 1st partition (FAT32)
        echo n
        echo p
        echo 1
        echo ${PART1_START}
        echo ${PART1_END}
        # 2nd partition (1st rootfs)
        echo n
        echo p
        echo 2
        echo ${PART2_START}
        echo ${PART2_END}
        # 3rd partition (2nd root)
        echo n
        echo p
        echo 3
        echo ${PART3_START}
        echo ${PART3_END}
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
        # COMMIT changes to image file
        echo p
        echo w

    ) | fdisk --compatibility=nondos --units=sectors ${SDIMG}

    dd if=/dev/zero of=fat.dat count=${PART1_SIZE}
    mkfs.vfat fat.dat

    # Create empty environment. Just so that the file is available.
    dd if=/dev/zero of=${IMAGE_BOOT_ENV_FILE} count=0 bs=1K seek=256
    mcopy -i fat.dat -v ${IMAGE_BOOT_ENV_FILE} ::
    rm -f ${IMAGE_BOOT_ENV_FILE}

    mcopy -i fat.dat -v ${DEPLOY_DIR_IMAGE}/uEnv.txt ::

    # Copy boot files to boot partition
    mcopy -i fat.dat -s ${DEPLOY_DIR_IMAGE}/${IMAGE_BOOT_FILES} ::

    dd if=fat.dat of=${SDIMG} seek=${PART1_START} conv=notrunc
    rm -f fat.dat

    dd if=${ROOTFS_IMG} of=${SDIMG} seek=${PART2_START} conv=notrunc
    dd if=${ROOTFS_IMG} of=${SDIMG} seek=${PART3_START} conv=notrunc

    # Print partition table, assert partitions are aligned and as expected
    #TODO
}
