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

IMAGE_DEPENDS_sdimg += "${IMAGE_DEPENDS_wic} dosfstools-native mtools-native rsync-native"

IMAGE_CMD_sdimg() {
    set -ex

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

    # create rootfs
    dd if=/dev/zero of=${WORKDIR}/rootfs.$FSTYPE count=0 seek=${MENDER_CALC_ROOTFS_SIZE} bs=1K
    mkfs.$FSTYPE -F -i 4096 ${WORKDIR}/rootfs.$FSTYPE -d ${IMAGE_ROOTFS}
    ln -sf ${WORKDIR}/rootfs.$FSTYPE ${WORKDIR}/active
    ln -sf ${WORKDIR}/rootfs.$FSTYPE ${WORKDIR}/inactive

    MENDER_PARTITION_ALIGNMENT_KB=$(expr ${MENDER_PARTITION_ALIGNMENT_MB} \* 1024)

    rm -rf "${WORKDIR}/data" || true
    mkdir -p "${WORKDIR}/data"

    if [ -n "${MENDER_DATA_PART_DIR}" ]; then
        rsync -a ${MENDER_DATA_PART_DIR}/* "${WORKDIR}/data"
        chown -R root:root "${WORKDIR}/data"
    fi

    if [ -f "${DEPLOY_DIR_IMAGE}/data.tar" ]; then
        ( cd "${WORKDIR}" && tar xf "${DEPLOY_DIR_IMAGE}/data.tar" )
    fi

    mkdir -p "${WORKDIR}/data/mender"
    echo "device_type=${MENDER_DEVICE_TYPE}" > "${WORKDIR}/data/mender/device_type"
    chmod 0444 "${WORKDIR}/data/mender/device_type"

    dd if=/dev/zero of="${WORKDIR}/data.$FSTYPE" count=0 bs=1M seek=${MENDER_DATA_PART_SIZE_MB}
    mkfs.$FSTYPE -F "${WORKDIR}/data.$FSTYPE" -d "${WORKDIR}/data" -L data

    wks="${WORKDIR}/mender-sdimg.wks"
    rm -f "$wks"
    if [ -n "${IMAGE_BOOTLOADER_FILE}" ]; then
        if [ $(expr ${IMAGE_BOOTLOADER_BOOTSECTOR_OFFSET} % 2) -ne 0 ]; then
            bbfatal "IMAGE_BOOTLOADER_BOOTSECTOR_OFFSET must be aligned to kB" \
                    "boundary (an even number)."
        fi
        bootloader_align_kb=$(expr $(expr ${IMAGE_BOOTLOADER_BOOTSECTOR_OFFSET} \* 512) / 1024)
        bootloader_size=$(stat -c '%s' "${DEPLOY_DIR_IMAGE}/${IMAGE_BOOTLOADER_FILE}")
        bootloader_end=$(expr $bootloader_align_kb \* 1024 + $bootloader_size)
        if [ $bootloader_end -gt ${MENDER_UBOOT_ENV_STORAGE_DEVICE_OFFSET} ]; then
            bberror "Size of bootloader specified in IMAGE_BOOTLOADER_FILE" \
                    "exceeds MENDER_UBOOT_ENV_STORAGE_DEVICE_OFFSET, which is" \
                    "reserved for U-Boot environment storage. Please raise it" \
                    "manually."
        fi
        cat >> "$wks" <<EOF
# embed bootloader
part --source rawcopy --sourceparams="file=${DEPLOY_DIR_IMAGE}/${IMAGE_BOOTLOADER_FILE}" --ondisk mmcblk0 --align $bootloader_align_kb --no-table
EOF
    fi

    if [ -n "${MENDER_UBOOT_ENV_STORAGE_DEVICE_OFFSET}" ]; then
        boot_env_align_kb=$(expr ${MENDER_UBOOT_ENV_STORAGE_DEVICE_OFFSET} / 1024)
        cat >> "$wks" <<EOF
part --source rawcopy --sourceparams="file=${DEPLOY_DIR_IMAGE}/uboot.env" --ondisk mmcblk0 --align $boot_env_align_kb --no-table
EOF
    fi

    cat >> "$wks" <<EOF
part /boot   --source bootimg-partition --ondisk mmcblk0 --fstype=vfat --label boot --align $MENDER_PARTITION_ALIGNMENT_KB --active --size ${MENDER_BOOT_PART_SIZE_MB}
part /       --source fsimage --sourceparams=file="${WORKDIR}/active" --ondisk mmcblk0 --label primary --align $MENDER_PARTITION_ALIGNMENT_KB
part         --source fsimage --sourceparams=file="${WORKDIR}/inactive" --ondisk mmcblk0 --label secondary --align $MENDER_PARTITION_ALIGNMENT_KB
part /data   --source fsimage --sourceparams=file="${WORKDIR}/data.$FSTYPE" --ondisk mmcblk0 --fstype=$FSTYPE --label data --align $MENDER_PARTITION_ALIGNMENT_KB
EOF

    echo "### Contents of wks file ###"
    cat "$wks"
    echo "### End of contents of wks file ###"

    # Call WIC
    outimgname="${IMGDEPLOYDIR}/${IMAGE_NAME}.sdimg"
    wicout="${IMGDEPLOYDIR}/${IMAGE_NAME}-sdimg"
    BUILDDIR="${TOPDIR}" wic create "$wks" --vars "${STAGING_DIR_TARGET}/imgdata/" -e "${IMAGE_BASENAME}" -o "$wicout/" ${WIC_CREATE_EXTRA_ARGS}
    mv "$wicout/build/$(basename "${wks%.wks}")"*.direct "$outimgname"
    rm -rf "$wicout/"

    ln -sfn "${IMAGE_NAME}.sdimg" "${DEPLOY_DIR_IMAGE}/${IMAGE_BASENAME}-${MACHINE}.sdimg"
}
