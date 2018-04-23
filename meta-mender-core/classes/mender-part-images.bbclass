# Class that creates an SD card image that boots under qemu's emulation
# for vexpress-a9 board. See the script mender-qemu for an example of
# how to boot the image.

# The partitioning scheme is:
#    part1: FAT partition with bootloader
#    part2: first rootfs, active
#    part3: second rootfs, inactive, mirror of first,
#           available as failsafe for when some update fails
#    part4: persistent data partition

python() {
    deprecated_vars = ['SDIMG_DATA_PART_DIR', 'SDIMG_DATA_PART_SIZE_MB',
                       'SDIMG_BOOT_PART_SIZE_MB', 'SDIMG_PARTITION_ALIGNMENT_MB']
    for varname in deprecated_vars:
        cur = d.getVar(varname, True)
        if cur:
            newvarname = varname.replace('SDIMG_', 'MENDER_')
            bb.fatal('Detected use of deprecated var %s, please replace it with %s in your setup' % (varname, newvarname))
}

inherit image
inherit image_types

# This normally defaults to .rootfs which is misleading as this is not a simple
# rootfs image and causes problems if one wants to use something like this:
#
#    IMAGE_FSTYPES += "sdimg.gz"
#
# Above assumes that the image name is:
#
#    ${IMAGE_NAME}${IMAGE_NAME_SUFFIX}.${type}
#
# Which results in a empty "gz" archive when using the default value, in our
# case IMAGE_NAME_SUFFIX should be empty as we do not use it when naming
# our image.
IMAGE_NAME_SUFFIX_sdimg = ""

mender_get_bootloader_offset() {
    # Copy the files to embed in the WIC image into ${WORKDIR} for exclusive access
    install -m 0644 "${DEPLOY_DIR_IMAGE}/${IMAGE_BOOTLOADER_FILE}" "${WORKDIR}/"

    if [ $(expr ${IMAGE_BOOTLOADER_BOOTSECTOR_OFFSET} % 2) -ne 0 ]; then
        bbfatal "IMAGE_BOOTLOADER_BOOTSECTOR_OFFSET must be aligned to kB" \
                "boundary (an even number)."
    fi
    local bootloader_offset_kb=$(expr $(expr ${IMAGE_BOOTLOADER_BOOTSECTOR_OFFSET} \* 512) / 1024)
    local bootloader_size=$(stat -c '%s' "${WORKDIR}/${IMAGE_BOOTLOADER_FILE}")
    local bootloader_end=$(expr $bootloader_offset_kb \* 1024 + $bootloader_size)
    if [ $bootloader_end -gt ${MENDER_UBOOT_ENV_STORAGE_DEVICE_OFFSET} ]; then
        bbfatal "Size of bootloader specified in IMAGE_BOOTLOADER_FILE" \
                "exceeds MENDER_UBOOT_ENV_STORAGE_DEVICE_OFFSET, which is" \
                "reserved for U-Boot environment storage. Please raise it" \
                "manually."
    fi

    echo $bootloader_offset_kb
}


################################################################################
# Block storage
################################################################################

mender_part_image() {
    suffix="$1"
    part_type="$2"
    boot_part_params="$3"

    set -ex

    mkdir -p "${WORKDIR}"

    # Workaround for the fact that the image builder requires this directory,
    # despite not using it. If "rm_work" is enabled, this directory won't always
    # exist.
    mkdir -p "${IMAGE_ROOTFS}"

    rm -rf "${WORKDIR}/data" || true
    mkdir -p "${WORKDIR}/data"

    if [ -n "${MENDER_DATA_PART_DIR}" ]; then
        rsync -a --no-owner --no-group ${MENDER_DATA_PART_DIR}/* "${WORKDIR}/data"
        chown -R root:root "${WORKDIR}/data"
    fi

    if [ -f "${DEPLOY_DIR_IMAGE}/data.tar" ]; then
        ( cd "${WORKDIR}" && tar xf "${DEPLOY_DIR_IMAGE}/data.tar" )
    fi

    mkdir -p "${WORKDIR}/data/mender"
    echo "device_type=${MENDER_DEVICE_TYPE}" > "${WORKDIR}/data/mender/device_type"
    chmod 0444 "${WORKDIR}/data/mender/device_type"

    dd if=/dev/zero of="${WORKDIR}/data.${ARTIFACTIMG_FSTYPE}" count=0 bs=1M seek=${MENDER_DATA_PART_SIZE_MB}
    mkfs.${ARTIFACTIMG_FSTYPE} -F "${WORKDIR}/data.${ARTIFACTIMG_FSTYPE}" -d "${WORKDIR}/data" -L data
    install -m 0644 "${WORKDIR}/data.${ARTIFACTIMG_FSTYPE}" "${DEPLOY_DIR_IMAGE}/"

    if ${@bb.utils.contains('DISTRO_FEATURES', 'mender-uboot', 'true', 'false', d)}; then
        # Copy the files to embed in the WIC image into ${WORKDIR} for exclusive access
        install -m 0644 "${DEPLOY_DIR_IMAGE}/uboot.env" "${WORKDIR}/"
    fi

    ondisk_dev="$(basename "${MENDER_STORAGE_DEVICE}")"

    wks="${WORKDIR}/mender-$suffix.wks"
    rm -f "$wks"
    if [ -n "${IMAGE_BOOTLOADER_FILE}" ]; then
        cat >> "$wks" <<EOF
# embed bootloader
part --source rawcopy --sourceparams="file=${WORKDIR}/${IMAGE_BOOTLOADER_FILE}" --ondisk "$ondisk_dev" --align $(mender_get_bootloader_offset) --no-table
EOF
    fi

    if ${@bb.utils.contains('DISTRO_FEATURES', 'mender-uboot', 'true', 'false', d)} && [ -n "${MENDER_UBOOT_ENV_STORAGE_DEVICE_OFFSET}" ]; then
        boot_env_align_kb=$(expr ${MENDER_UBOOT_ENV_STORAGE_DEVICE_OFFSET} / 1024)
        cat >> "$wks" <<EOF
part --source rawcopy --sourceparams="file=${WORKDIR}/uboot.env" --ondisk "$ondisk_dev" --align $boot_env_align_kb --no-table
EOF
    fi

    if [ $(expr ${MENDER_PARTITION_ALIGNMENT} % 1024 || true) -ne 0 ]; then
        bbfatal "MENDER_PARTITION_ALIGNMENT must be KiB aligned when using partition table."
    fi

    alignment_kb=$(expr ${MENDER_PARTITION_ALIGNMENT} / 1024)

    if [ "${MENDER_BOOT_PART_SIZE_MB}" -ne "0" ]; then
        cat >> "$wks" <<EOF
part $boot_part_params --ondisk "$ondisk_dev" --fstype=vfat --label boot --align $alignment_kb --active --fixed-size ${MENDER_BOOT_PART_SIZE_MB}
EOF
    fi

    cat >> "$wks" <<EOF
part --source rootfs --ondisk "$ondisk_dev" --fstype=${ARTIFACTIMG_FSTYPE} --label primary --align $alignment_kb --fixed-size ${MENDER_CALC_ROOTFS_SIZE}k
part --source rootfs --ondisk "$ondisk_dev" --fstype=${ARTIFACTIMG_FSTYPE} --label secondary --align $alignment_kb --fixed-size ${MENDER_CALC_ROOTFS_SIZE}k
part --source rawcopy --sourceparams=file="${WORKDIR}/data.${ARTIFACTIMG_FSTYPE}" --ondisk "$ondisk_dev" --fstype=${ARTIFACTIMG_FSTYPE} --label data --align $alignment_kb --fixed-size ${MENDER_DATA_PART_SIZE_MB}
bootloader --ptable $part_type
EOF

    echo "### Contents of wks file ###"
    cat "$wks"
    echo "### End of contents of wks file ###"

    # Call WIC
    outimgname="${IMGDEPLOYDIR}/${IMAGE_NAME}.$suffix"
    wicout="${IMGDEPLOYDIR}/${IMAGE_NAME}-$suffix"
    BUILDDIR="${TOPDIR}" wic create "$wks" --vars "${STAGING_DIR}/${MACHINE}/imgdata/" -e "${IMAGE_BASENAME}" -o "$wicout/" ${WIC_CREATE_EXTRA_ARGS}
    mv "$wicout/$(basename "${wks%.wks}")"*.direct "$outimgname"
    ln -sfn "${IMAGE_NAME}.$suffix" "${IMGDEPLOYDIR}/${IMAGE_NAME}${IMAGE_NAME_SUFFIX}.$suffix"
    rm -rf "$wicout/"

    ln -sfn "${IMAGE_NAME}.$suffix" "${IMGDEPLOYDIR}/${IMAGE_BASENAME}-${MACHINE}.$suffix"
}

IMAGE_CMD_sdimg() {
    mender_part_image sdimg msdos "--source bootimg-partition"
}
IMAGE_CMD_uefiimg() {
    mender_part_image uefiimg gpt "--source bootimg-partition --part-type EF00"
}

addtask do_rootfs_wicenv after do_image before do_image_sdimg
addtask do_rootfs_wicenv after do_image before do_image_uefiimg

do_image_sdimg[depends] += " \
    ${@d.getVarFlag('do_image_wic', 'depends', False)} \
    wic-tools:do_populate_sysroot \
    dosfstools-native:do_populate_sysroot \
    mtools-native:do_populate_sysroot \
    rsync-native:do_populate_sysroot \
    virtual/bootloader:do_deploy \
"

do_image_uefiimg[depends] += " \
    ${@d.getVarFlag('do_image_wic', 'depends', False)} \
    wic-tools:do_populate_sysroot \
    dosfstools-native:do_populate_sysroot \
    mtools-native:do_populate_sysroot \
    rsync-native:do_populate_sysroot \
    virtual/bootloader:do_deploy \
    ${@bb.utils.contains('DISTRO_FEATURES', 'mender-grub', 'grub-efi:do_deploy', '', d)} \
"
do_image_sdimg[depends] += " ${@bb.utils.contains('SOC_FAMILY', 'rpi', 'bcm2835-bootfiles:do_populate_sysroot', '', d)}"

# This isn't actually a dependency, but a way to avoid sdimg and uefiimg
# building simultaneously, since wic will use the same file names in both, and
# in parallel builds this is a recipe for disaster.
IMAGE_TYPEDEP_uefiimg_append = "${@bb.utils.contains('IMAGE_FSTYPES', 'sdimg', ' sdimg', '', d)}"


################################################################################
# Flash storage
################################################################################

mender_flash_mtdpart() {
    local file="$1"
    local size="$2"
    local kbsize="$3"
    local kboffset="$4"
    local name="$5"

    if [ "$size" = "-" ]; then
        # Remaining space.
        local total_space_kb=$(expr ${MENDER_STORAGE_TOTAL_SIZE_MB} \* 1024)
        kbsize=$(expr $total_space_kb - $kboffset)
        size=$(expr $kbsize \* 1024)
    fi

    if [ "$file" != "/dev/zero" ]; then
        local file_size=$(stat -Lc '%s' "$file")
        if [ $file_size -gt $size ]; then
            bbfatal "$file is too big to fit inside '$name' mtdpart of size $size."
        fi
    fi
    dd if="$file" \
        of="${IMGDEPLOYDIR}/${IMAGE_NAME}.mtdimg" \
        bs=1024 \
        seek=$kboffset \
        count=$kbsize
}

IMAGE_CMD_mtdimg() {
    set -ex

    # We don't actually use the result from this one, it's only to trigger a
    # warning or error if the variable is not correctly set.
    mender_get_mtdparts

    ${@mender_make_mtdparts_shell_array(d)}

    local remaining_encountered=0
    local i=0
    while [ $i -lt $mtd_count ]; do
        eval local name="\"\$mtd_names_$i\""
        eval local size="\"\$mtd_sizes_$i\""
        eval local kbsize="\"\$mtd_kbsizes_$i\""
        eval local kboffset="\"\$mtd_kboffsets_$i\""

        if [ "$name" = "u-boot" ]; then
            if [ -n "${IMAGE_BOOTLOADER_FILE}" ]; then
                mender_flash_mtdpart "${DEPLOY_DIR_IMAGE}/${IMAGE_BOOTLOADER_FILE}" $size $kbsize $kboffset $name
            else
                bbwarn "There is a 'u-boot' mtdpart, but IMAGE_BOOTLOADER_FILE is undefined. Filling with zeros."
                mender_flash_mtdpart "/dev/zero" $size $kbsize $kboffset $name
            fi
        elif [ "$name" = "u-boot-env" ]; then
            mender_flash_mtdpart "${DEPLOY_DIR_IMAGE}/uboot.env" $size $kbsize $kboffset $name
        elif [ "$name" = "ubi" ]; then
            mender_flash_mtdpart "${IMGDEPLOYDIR}/${IMAGE_BASENAME}-${MACHINE}.ubimg" $size $kbsize $kboffset $name
        else
            bbwarn "Don't know how to flash mtdparts '$name'. Filling with zeros."
            mender_flash_mtdpart "/dev/zero" $size $kbsize $kboffset $name
        fi

        i=$(expr $i + 1)
    done

    ln -sfn "${IMAGE_NAME}.mtdimg" "${IMGDEPLOYDIR}/${IMAGE_BASENAME}-${MACHINE}.mtdimg"
}

IMAGE_TYPEDEP_mtdimg_append = " ubimg"
