inherit mender-image-buildinfo

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
SDIMG_BOOT_PART_SIZE_MB ?= "16"

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
#IMAGE_UENV_TXT_FILE ?= "uEnv.txt"
IMAGE_UENV_TXT_FILE ?= ""

IMAGE_BOOT_FILES_append = " ${IMAGE_UENV_TXT_FILE}"

# This will be embedded into the boot sector, or close to the boot sector, where
# exactly depends on the offset variable.
IMAGE_BOOTLOADER_FILE ?= "u-boot.${UBOOT_SUFFIX}"
# Offset of bootloader, in sectors (512 bytes).
IMAGE_BOOTLOADER_BOOTSECTOR_OFFSET ?= "2"

########## CONFIGURATION END ##########

inherit image
inherit image_types

addtask do_rootfs_wicenv after do_image before do_image_sdimg

WKS_FULL_PATH = "${WORKDIR}/mender-sdimg.wks"

python() {
    fslist = d.getVar('IMAGE_FSTYPES', None).split()
    for fs in fslist:
        if fs in ["ext2", "ext3", "ext4"]:
            # We need to have the filesystem image generated already. Make it
            # dependent on all image types we support.
            d.setVar('IMAGE_TYPEDEP_sdimg_append', " " + fs)
}

IMAGE_DEPENDS_sdimg = "${IMAGE_DEPENDS_wic} dosfstools-native mtools-native"

IMAGE_CMD_sdimg() {
    set -e

    # For some reason, logging is not working correctly inside IMAGE_CMD bodies,
    # so wrap all logging in these functions that also have an echo. This won't
    # prevent warnings from being hidden deep in log files, but there is nothing
    # we can do about that.
    sdimg_warn() {
        echo "$@"
        bbwarn "$@"
    }
    sdimg_fatal() {
        echo "$@"
        bbfatal "$@"
    }

    # Figure out which filesystem type to use.
    FSTYPE=
    for fs in ${IMAGE_FSTYPES}
    do
        case $fs in
        ext2|ext3|ext4)
            if [ -n "$FSTYPE" ]
            then
                sdimg_warn "More than one filesystem candidate found in IMAGE_FSTYPES = '${IMAGE_FSTYPES}'. Using $FSTYPE and ignoring $fs."
            else
                FSTYPE=$fs
            fi
            ;;
        esac
    done
    if [ -z "$FSTYPE" ]
    then
        sdimg_fatal "No filesystem appropriate for sdimg was found in IMAGE_FSTYPES = '${IMAGE_FSTYPES}'."
    fi

    mkdir -p "${WORKDIR}"

    # Workaround for the fact that the image builder requires this directory,
    # despite not using it. If "rm_work" is enabled, this directory won't always
    # exist.
    mkdir -p "${IMAGE_ROOTFS}"

    # Workaround for the fact the wic deletes its inputs (WTF??). These links
    # are disposable.
    ln -sfn "${DEPLOY_DIR_IMAGE}/${IMAGE_BASENAME}-${MACHINE}.$FSTYPE" \
        "${WORKDIR}/active.$FSTYPE"
    ln -sfn "${DEPLOY_DIR_IMAGE}/${IMAGE_BASENAME}-${MACHINE}.$FSTYPE" \
        "${WORKDIR}/inactive.$FSTYPE"

    PART1_SIZE=$(expr ${SDIMG_BOOT_PART_SIZE_MB} \* 2048)
    SDIMG_PARTITION_ALIGNMENT_KB=$(expr ${SDIMG_PARTITION_ALIGNMENT_MB} \* 1024)

    dd if=/dev/zero of="${WORKDIR}/boot.vfat" count=${PART1_SIZE}
    mkfs.vfat "${WORKDIR}/boot.vfat"

    # Copy boot files to boot partition
    IMAGE_BOOT_FILES="${IMAGE_BOOT_FILES}"
    for entry in $IMAGE_BOOT_FILES
    do
        # Handle special ';' syntax. See documentation for IMAGE_BOOT_FILES.
        dir="${entry#*;}"
        if [ "$dir" = "$entry" ]
        then
            dir=
        fi
        file="${entry%;*}"
        mcopy -i "${WORKDIR}/boot.vfat" -s ${DEPLOY_DIR_IMAGE}/$file ::$dir
    done

    rm -rf "${WORKDIR}/data" || true
    if [ -n "${SDIMG_DATA_PART_DIR}" ]; then
        cp -a "${SDIMG_DATA_PART_DIR}" "${WORKDIR}/data"
    else
        mkdir -p "${WORKDIR}/data"
    fi

    # The OpenSSL certificates should go here:
    echo "dummy certificate" > "${WORKDIR}/data/mender.cert"

    dd if=/dev/zero of="${WORKDIR}/data.$FSTYPE" count=0 bs=1M seek=${SDIMG_DATA_PART_SIZE_MB}
    mkfs.$FSTYPE -F "${WORKDIR}/data.$FSTYPE" -d "${WORKDIR}/data"

    cat > "${WORKDIR}/mender-sdimg.wks" <<EOF
part /uboot  --source fsimage --sourceparams=file="${WORKDIR}/boot.vfat"     --ondisk mmcblk0 --fstype=vfat --label boot     --align $SDIMG_PARTITION_ALIGNMENT_KB --active
part /       --source fsimage --sourceparams=file="${WORKDIR}/active.$FSTYPE"   --ondisk mmcblk0 --fstype=$FSTYPE --label platform --align $SDIMG_PARTITION_ALIGNMENT_KB
part /       --source fsimage --sourceparams=file="${WORKDIR}/inactive.$FSTYPE" --ondisk mmcblk0 --fstype=$FSTYPE --label platform --align $SDIMG_PARTITION_ALIGNMENT_KB
part /data   --source fsimage --sourceparams=file="${WORKDIR}/data.$FSTYPE"     --ondisk mmcblk0 --fstype=$FSTYPE --label data     --align $SDIMG_PARTITION_ALIGNMENT_KB

# Note: "bootloader" appears to be useless in this context, but the wic
# framework requires that it be present.
bootloader --timeout=10  --append=""
EOF

    # Call WIC
    IMAGE_CMD_wic

    # Embed boot loader in image, offset relative to boot sector.
    if [ -n "${IMAGE_BOOTLOADER_FILE}" ]; then
        if [ $(expr ${SDIMG_PARTITION_ALIGNMENT_MB} \* 1048576 - ${IMAGE_BOOTLOADER_BOOTSECTOR_OFFSET} \* 512) -lt $(stat -c %s ${IMAGE_BOOTLOADER_FILE}) ]; then
            sdimg_fatal "Not enough space to embed boot loader in boot sector. Increase SDIMG_PARTITION_ALIGNMENT_MB."
        fi

        dd if="${DEPLOY_DIR_IMAGE}/${IMAGE_BOOTLOADER_FILE}" of="${DEPLOY_DIR_IMAGE}/${IMAGE_NAME}.rootfs.wic" bs=512 seek=${IMAGE_BOOTLOADER_BOOTSECTOR_OFFSET} conv=notrunc
    fi

    mv "${DEPLOY_DIR_IMAGE}/${IMAGE_NAME}.rootfs.wic" "${DEPLOY_DIR_IMAGE}/${IMAGE_NAME}.sdimg"
    ln -sfn "${IMAGE_NAME}.sdimg" "${DEPLOY_DIR_IMAGE}/${IMAGE_BASENAME}-${MACHINE}.sdimg"
}
