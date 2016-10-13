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
MENDER_DATA_PART_DIR ?= ""

# Size of the data partition, which is preserved across updates.
MENDER_DATA_PART_SIZE_MB ?= "128"

# Size of the first (FAT) partition, that contains the bootloader
MENDER_BOOT_PART_SIZE_MB ?= "16"

# For performance reasons, we try to align the partitions to the SD
# card's erase block. It is impossible to know this information with
# certainty, but one way to find out is to run the "flashbench" tool on
# your SD card and study the results. If you do, feel free to override
# this default.
#
# 8MB alignment is a safe setting that might waste some space if the
# erase block is smaller.
MENDER_PARTITION_ALIGNMENT_MB ?= "8"

python() {
    deprecated_vars = ['SDIMG_DATA_PART_DIR', 'SDIMG_DATA_PART_SIZE_MB',
                       'SDIMG_BOOT_PART_SIZE_MB', 'SDIMG_PARTITION_ALIGNMENT_MB']
    for varname in deprecated_vars:
        cur = d.getVar(varname, True)
        if cur:
            newvarname = varname.replace('SDIMG_', 'MENDER_')
            bb.fatal('Detected use of deprecated var %s, please replace it with %s in your setup' % (varname, newvarname))
}

# u-boot environment file
#IMAGE_UENV_TXT_FILE ?= "uEnv.txt"
IMAGE_UENV_TXT_FILE ?= ""

IMAGE_BOOT_FILES_append = " ${IMAGE_UENV_TXT_FILE}"

# make sure to provide a weak default
UBOOT_SUFFIX ??= "bin"

# This will be embedded into the boot sector, or close to the boot sector, where
# exactly depends on the offset variable. Since it is a machine specific
# setting, the default value is an empty string.
IMAGE_BOOTLOADER_FILE ?= ""

# Offset of bootloader, in sectors (512 bytes).
IMAGE_BOOTLOADER_BOOTSECTOR_OFFSET ?= "2"

# This is missing in krogoth, so define it ourselves in order to avoid having to
# change all the places that reference it.
IMGDEPLOYDIR = "${WORKDIR}/deploy-${PN}-image-complete"

########## CONFIGURATION END ##########

inherit image
inherit image_types

addtask do_rootfs_wicenv after do_image before do_image_sdimg

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

    PART1_SIZE=$(expr ${MENDER_BOOT_PART_SIZE_MB} \* 2048)
    MENDER_PARTITION_ALIGNMENT_KB=$(expr ${MENDER_PARTITION_ALIGNMENT_MB} \* 1024)

    rm -rf "${WORKDIR}/data" || true
    if [ -n "${MENDER_DATA_PART_DIR}" ]; then
        cp -a "${MENDER_DATA_PART_DIR}" "${WORKDIR}/data"
    else
        mkdir -p "${WORKDIR}/data"
    fi

    # The OpenSSL certificates should go here:
    echo "dummy certificate" > "${WORKDIR}/data/mender.cert"

    dd if=/dev/zero of="${WORKDIR}/data.$FSTYPE" count=0 bs=1M seek=${MENDER_DATA_PART_SIZE_MB}
    mkfs.$FSTYPE -F "${WORKDIR}/data.$FSTYPE" -d "${WORKDIR}/data"

    wks="${WORKDIR}/mender-sdimg.wks"
    rm -f "$wks"
    if [ -n "${IMAGE_BOOTLOADER_FILE}" ]; then
        bootloader_align_kb=$(expr $(expr ${IMAGE_BOOTLOADER_BOOTSECTOR_OFFSET} \* 512) / 1024)
        cat >> "$wks" <<EOF
# embed bootloader
part --source rawcopy --sourceparams="file=${DEPLOY_DIR_IMAGE}/${IMAGE_BOOTLOADER_FILE}" --ondisk mmcblk0 --align $bootloader_align_kb --no-table
EOF
    fi

    cat >> "$wks" <<EOF
part /boot   --source bootimg-partition --ondisk mmcblk0 --fstype=vfat --label boot --align $MENDER_PARTITION_ALIGNMENT_KB --active --size ${MENDER_BOOT_PART_SIZE_MB}
part /       --source rootfs --ondisk mmcblk0 --fstype=$FSTYPE --label primary --align $MENDER_PARTITION_ALIGNMENT_KB
part /       --source rootfs --ondisk mmcblk0 --fstype=$FSTYPE --label secondary --align $MENDER_PARTITION_ALIGNMENT_KB
part /data   --source fsimage --sourceparams=file="${WORKDIR}/data.$FSTYPE"     --ondisk mmcblk0 --fstype=$FSTYPE --label data     --align $MENDER_PARTITION_ALIGNMENT_KB

EOF

    # Call WIC
    outimgname="${DEPLOY_DIR_IMAGE}/${IMAGE_NAME}.sdimg"
    wicout="${IMGDEPLOYDIR}/${IMAGE_NAME}-sdimg"
    BUILDDIR="${TOPDIR}" wic create "$wks" --vars "${STAGING_DIR_TARGET}/imgdata/" -e "${IMAGE_BASENAME}" -o "$wicout/" ${WIC_CREATE_EXTRA_ARGS}
    mv "$wicout/build/$(basename "${wks%.wks}")"*.direct "$outimgname"
    rm -rf "$wicout/"

    ln -sfn "${IMAGE_NAME}.sdimg" "${DEPLOY_DIR_IMAGE}/${IMAGE_BASENAME}-${MACHINE}.sdimg"
}
