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
IMAGE_NAME_SUFFIX = ""


################################################################################
# Block storage
################################################################################

# Take the content from the rootfs that is going into the boot partition, coming
# from MENDER_BOOT_PART_MOUNT_LOCATION, and merge with the files from
# IMAGE_BOOT_FILES, following the format from the official Yocto documentation.
mender_merge_bootfs_and_image_boot_files() {
    W="${WORKDIR}/bootfs.${BB_CURRENTTASK}"
    rm -rf "$W"

    cp -al "${IMAGE_ROOTFS}/${MENDER_BOOT_PART_MOUNT_LOCATION}" "$W"

    # Put in variable to avoid expansion and ';' being parsed by shell.
    image_boot_files="${IMAGE_BOOT_FILES}"
    for entry in $image_boot_files; do
        if echo "$entry" | grep -q ";"; then
            dest="$(echo "$entry" | sed -e 's/[^;]*;//')"
            entry="$(echo "$entry" | sed -e 's/;.*//')"
        else
            dest="./"
        fi
        if echo "$dest" | grep -q '/$'; then
            dest_is_dir=1
            mkdir -p "$W/$dest"
        else
            dest_is_dir=0
            mkdir -p "$(dirname "$W/$dest")"
        fi

        # Use extra for loop so we can check conflict for each file.
        for file in ${DEPLOY_DIR_IMAGE}/$entry; do
            if [ $dest_is_dir -eq 1 ]; then
                destfile="$W/$dest$(basename $file)"
            else
                destfile="$W/$dest"
            fi
            if [ -e "$destfile" ]; then
                bbfatal "$destfile already exists in boot partition. Please verify that packages do not put files in the boot partition that conflict with IMAGE_BOOT_FILES."
            fi
            cp -l "$file" "$destfile"
        done
    done
}

def mender_wic_exclude_path_options(rootfs, exclude_path):
    exclude_path = exclude_path.strip()

    existing_exclude_paths = ""
    for path in exclude_path.split():
        if os.path.lexists(os.path.realpath(os.path.join(rootfs, path))):
           existing_exclude_paths += path + " "

    if existing_exclude_paths:
        return "--exclude-path %s" % existing_exclude_paths
    else:
        return ""

mender_part_image() {
    suffix="$1"
    part_type="$2"
    boot_part_params="$3"

    set -ex

    mkdir -p "${WORKDIR}"

    if ${@bb.utils.contains('DISTRO_FEATURES', 'mender-uboot', 'true', 'false', d)}; then
        # Copy the files to embed in the WIC image into ${WORKDIR} for exclusive access
        install -m 0644 "${DEPLOY_DIR_IMAGE}/uboot.env" "${WORKDIR}/"
    fi

    ondisk_dev="$(basename "${MENDER_STORAGE_DEVICE}")"

    wks="${WORKDIR}/mender-$suffix.wks"
    rm -f "$wks"
    if [ -n "${MENDER_IMAGE_BOOTLOADER_FILE}" ]; then
        # Copy the files to embed in the WIC image into ${WORKDIR} for exclusive access
        install -m 0644 "${DEPLOY_DIR_IMAGE}/${MENDER_IMAGE_BOOTLOADER_FILE}" "${WORKDIR}/"

        if [ $(expr ${MENDER_IMAGE_BOOTLOADER_BOOTSECTOR_OFFSET} % 2) -ne 0 ]; then
            # wic doesn't support fractions of kiB, so we need to do some tricks
            # when we are at an odd sector: Create a new bootloader file that
            # lacks the first 512 bytes, write that at the next even sector,
            # which coincides with a whole kiB, and then write the missing
            # sector manually afterwards.
            bootloader_sector=$(expr ${MENDER_IMAGE_BOOTLOADER_BOOTSECTOR_OFFSET} + 1)
            bootloader_file=${WORKDIR}/${MENDER_IMAGE_BOOTLOADER_FILE}-partial
            dd if=${WORKDIR}/${MENDER_IMAGE_BOOTLOADER_FILE} of=$bootloader_file skip=1
        else
            bootloader_sector=${MENDER_IMAGE_BOOTLOADER_BOOTSECTOR_OFFSET}
            bootloader_file=${WORKDIR}/${MENDER_IMAGE_BOOTLOADER_FILE}
        fi
        bootloader_align_kb=$(expr $(expr $bootloader_sector \* 512) / 1024)
        bootloader_size=$(stat -c '%s' "$bootloader_file")
        bootloader_end=$(expr $bootloader_align_kb \* 1024 + $bootloader_size)
        if [ $bootloader_end -gt ${MENDER_UBOOT_ENV_STORAGE_DEVICE_OFFSET} ]; then
            bberror "Size of bootloader specified in MENDER_IMAGE_BOOTLOADER_FILE" \
                    "exceeds MENDER_UBOOT_ENV_STORAGE_DEVICE_OFFSET, which is" \
                    "reserved for U-Boot environment storage. Please raise it" \
                    "manually."
        fi
        cat >> "$wks" <<EOF
# embed bootloader
part --source rawcopy --sourceparams="file=$bootloader_file" --ondisk "$ondisk_dev" --align $bootloader_align_kb --no-table
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

    # remove leading and trailing spaces
    IMAGE_BOOT_FILES_STRIPPED=$(echo "${IMAGE_BOOT_FILES}" | sed -r 's/(^\s*)|(\s*$)//g')

    if [ "${MENDER_BOOT_PART_SIZE_MB}" -ne "0" ]; then
        mender_merge_bootfs_and_image_boot_files
        cat >> "$wks" <<EOF
part --source rootfs --rootfs-dir ${WORKDIR}/bootfs.${BB_CURRENTTASK} --ondisk "$ondisk_dev" --fstype=vfat --label boot --align $alignment_kb --fixed-size ${MENDER_BOOT_PART_SIZE_MB} --active
EOF
    elif [ -n "$IMAGE_BOOT_FILES_STRIPPED" ]; then
        bbwarn "MENDER_BOOT_PART_SIZE_MB is set to zero, but IMAGE_BOOT_FILES is not empty. The files are being omitted from the image."
    fi

    exclude_path_options="${@mender_wic_exclude_path_options('${IMAGE_ROOTFS}', '${IMAGE_ROOTFS_EXCLUDE_PATH}')}"

    cat >> "$wks" <<EOF
part --source rootfs --ondisk "$ondisk_dev" --fstype=${ARTIFACTIMG_FSTYPE} --label primary --align $alignment_kb --fixed-size ${MENDER_CALC_ROOTFS_SIZE}k $exclude_path_options
part --source rootfs --ondisk "$ondisk_dev" --fstype=${ARTIFACTIMG_FSTYPE} --label secondary --align $alignment_kb --fixed-size ${MENDER_CALC_ROOTFS_SIZE}k $exclude_path_options
part --source rootfs --rootfs-dir ${IMAGE_ROOTFS}/data --ondisk "$ondisk_dev" --fstype=${ARTIFACTIMG_FSTYPE} --label data --align $alignment_kb --fixed-size ${MENDER_DATA_PART_SIZE_MB}
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

    if [ -n "${MENDER_IMAGE_BOOTLOADER_FILE}" ] && [ ${MENDER_IMAGE_BOOTLOADER_BOOTSECTOR_OFFSET} -ne $bootloader_sector ]; then
        # We need to write the first sector of the bootloader. See comment above
        # where bootloader_sector is set.
        dd if=${WORKDIR}/${MENDER_IMAGE_BOOTLOADER_FILE} of="$outimgname" seek=${MENDER_IMAGE_BOOTLOADER_BOOTSECTOR_OFFSET} count=1 conv=notrunc
    fi

    if [ -n "${MENDER_MBR_BOOTLOADER_FILE}" ]; then
        dd if="${DEPLOY_DIR_IMAGE}/${MENDER_MBR_BOOTLOADER_FILE}" of="$outimgname" bs=${MENDER_MBR_BOOTLOADER_LENGTH} count=1 conv=notrunc
    fi

    rm -rf "$wicout/"

    # Pad the image up to the alignment. This matters mostly for the emulator,
    # which uses the file size to determine the size of the storage device,
    # which must be a multiple of its device block size. However, it might be
    # beneficial for real storage media as well, to make sure the final sector
    # is cleared out when flashing the image. May increase image size slightly,
    # but should compress well!
    alignment=${MENDER_PARTITION_ALIGNMENT}
    pad_size=$(expr \( $(stat -c %s "$outimgname") + $alignment - 1 \) / $alignment \* $alignment)
    truncate -s $pad_size "$outimgname"

    # If we padded above, and the partition table type is GPT, we need to
    # relocate the trailing backup header to the new end to avoid warnings.
    if [ "$part_type" = "gpt" ]; then
        sgdisk -e "$outimgname"
    fi

    if ${@bb.utils.contains('DISTRO_FEATURES', 'mender-partuuid', 'true', 'false', d)}; then
        if [ "$part_type" = "gpt" ]; then
            # Set Fixed PARTUUID for all devices
            sgdisk -u ${MENDER_BOOT_PART_NUMBER}:${@mender_get_partuuid_from_device(d, '${MENDER_BOOT_PART}')} "$outimgname"
            sgdisk -u ${MENDER_ROOTFS_PART_A_NUMBER}:${@mender_get_partuuid_from_device(d, '${MENDER_ROOTFS_PART_A}')} "$outimgname"
            sgdisk -u ${MENDER_ROOTFS_PART_B_NUMBER}:${@mender_get_partuuid_from_device(d, '${MENDER_ROOTFS_PART_B}')} "$outimgname"
            sgdisk -u ${MENDER_DATA_PART_NUMBER}:${@mender_get_partuuid_from_device(d, '${MENDER_DATA_PART}')} "$outimgname"
        else
            diskIdent=$(echo ${@mender_get_partuuid_from_device(d, '${MENDER_ROOTFS_PART_A}')} | cut -d- -f1)
            # For MBR Set the Disk Identifier.  Drives follow the pattern of <Disk Identifier>-<Part Number>
            (
                echo x                              # Enter expert mode
                echo i                              # Set disk identifier
                echo 0x${diskIdent}                 # Identifier
                echo r                              # Exit expert mode
                echo w                              # Write changes
            ) | fdisk ${outimgname}
        fi
    fi
}

IMAGE_CMD_sdimg() {
    mender_part_image sdimg msdos "--source bootimg-partition"
}
IMAGE_CMD_uefiimg() {
    mender_part_image uefiimg gpt "--source bootimg-partition --part-type EF00"
}
IMAGE_CMD_biosimg() {
    mender_part_image biosimg msdos "--source bootimg-partition"
}
IMAGE_CMD_gptimg() {
    mender_part_image gptimg gpt "--source bootimg-partition"
}


addtask do_rootfs_wicenv after do_image before do_image_sdimg
addtask do_rootfs_wicenv after do_image before do_image_uefiimg
addtask do_rootfs_wicenv after do_image before do_image_biosimg
addtask do_rootfs_wicenv after do_image before do_image_gptimg

_MENDER_PART_IMAGE_DEPENDS = " \
    ${@d.getVarFlag('do_image_wic', 'depends', False)} \
    coreutils-native:do_populate_sysroot \
    wic-tools:do_populate_sysroot \
    dosfstools-native:do_populate_sysroot \
    mtools-native:do_populate_sysroot \
"


# This is needed because by default 'mender-grub' feature is used on ARM, but
# it still uses U-boot as an EFI provider/launcher and requires it to be
# present. We can not add this to '_append_mender-grub' because this is also
# used by x86 based devices which normally do not use U-boot.
#
# This assumes that U-boot is used on ARM, this could become problematic
# if we add support for other bootloaders on ARM, e.g Barebox.
_MENDER_PART_IMAGE_DEPENDS_append_arm =     " u-boot:do_deploy"
_MENDER_PART_IMAGE_DEPENDS_append_aarch64 = " u-boot:do_deploy"

_MENDER_PART_IMAGE_DEPENDS_append_mender-uboot = " u-boot:do_deploy"
_MENDER_PART_IMAGE_DEPENDS_append_mender-grub = " grub-efi:do_deploy"
_MENDER_PART_IMAGE_DEPENDS_append_mender-grub_mender-bios = " grub:do_deploy"

do_image_sdimg[depends] += "${_MENDER_PART_IMAGE_DEPENDS}"
do_image_sdimg[depends] += " ${@bb.utils.contains('SOC_FAMILY', 'rpi', 'bcm2835-bootfiles:do_populate_sysroot', '', d)}"

do_image_uefiimg[depends] += "${_MENDER_PART_IMAGE_DEPENDS} \
                              gptfdisk-native:do_populate_sysroot"

do_image_biosimg[depends] += "${_MENDER_PART_IMAGE_DEPENDS}"

do_image_gptimg[depends] += "${_MENDER_PART_IMAGE_DEPENDS}"
# This isn't actually a dependency, but a way to avoid sdimg and uefiimg
# building simultaneously, since wic will use the same file names in both, and
# in parallel builds this is a recipe for disaster.
IMAGE_TYPEDEP_uefiimg_append = "${@bb.utils.contains('IMAGE_FSTYPES', 'sdimg', ' sdimg', '', d)}"
# And same here.
IMAGE_TYPEDEP_biosimg_append = "${@bb.utils.contains('IMAGE_FSTYPES', 'sdimg', ' sdimg', '', d)} ${@bb.utils.contains('IMAGE_FSTYPES', 'uefiimg', ' uefiimg', '', d)}"
# And same here.
IMAGE_TYPEDEP_gptimg_append = "${@bb.utils.contains('IMAGE_FSTYPES', 'sdimg', ' sdimg', '', d)} \
                               ${@bb.utils.contains('IMAGE_FSTYPES', 'uefiimg', ' uefiimg', '', d)} \
                               ${@bb.utils.contains('IMAGE_FSTYPES', 'biosimg', ' biosimg', '', d)}"

# So that we can use the files from excluded paths in the full images.
do_image_sdimg[respect_exclude_path] = "0"
do_image_uefiimg[respect_exclude_path] = "0"
do_image_biosimg[respect_exclude_path] = "0"
do_image_gptimg[respect_exclude_path] = "0"

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
    # Flash zeros first to make sure that a shorter ubimg doesn't truncate the
    # write.
    dd if="/dev/zero" \
        of="${IMGDEPLOYDIR}/${IMAGE_NAME}.mtdimg" \
        bs=1024 \
        seek=$kboffset \
        count=$kbsize \
        conv=notrunc
    dd if="$file" \
        of="${IMGDEPLOYDIR}/${IMAGE_NAME}.mtdimg" \
        bs=1024 \
        seek=$kboffset \
        count=$kbsize \
        conv=notrunc
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
            if [ -n "${MENDER_IMAGE_BOOTLOADER_FILE}" ]; then
                mender_flash_mtdpart "${DEPLOY_DIR_IMAGE}/${MENDER_IMAGE_BOOTLOADER_FILE}" $size $kbsize $kboffset $name
            else
                bbwarn "There is a 'u-boot' mtdpart, but MENDER_IMAGE_BOOTLOADER_FILE is undefined. Filling with zeros."
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
