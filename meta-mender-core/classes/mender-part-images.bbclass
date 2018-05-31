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
        # Copy the files to embed in the WIC image into ${WORKDIR} for exclusive access
        install -m 0644 "${DEPLOY_DIR_IMAGE}/${IMAGE_BOOTLOADER_FILE}" "${WORKDIR}/"

        if [ $(expr ${IMAGE_BOOTLOADER_BOOTSECTOR_OFFSET} % 2) -ne 0 ]; then
            bbfatal "IMAGE_BOOTLOADER_BOOTSECTOR_OFFSET must be aligned to kB" \
                    "boundary (an even number)."
        fi
        bootloader_align_kb=$(expr $(expr ${IMAGE_BOOTLOADER_BOOTSECTOR_OFFSET} \* 512) / 1024)
        bootloader_size=$(stat -c '%s' "${WORKDIR}/${IMAGE_BOOTLOADER_FILE}")
        bootloader_end=$(expr $bootloader_align_kb \* 1024 + $bootloader_size)
        if [ $bootloader_end -gt ${MENDER_UBOOT_ENV_STORAGE_DEVICE_OFFSET} ]; then
            bberror "Size of bootloader specified in IMAGE_BOOTLOADER_FILE" \
                    "exceeds MENDER_UBOOT_ENV_STORAGE_DEVICE_OFFSET, which is" \
                    "reserved for U-Boot environment storage. Please raise it" \
                    "manually."
        fi
        cat >> "$wks" <<EOF
# embed bootloader
part --source rawcopy --sourceparams="file=${WORKDIR}/${IMAGE_BOOTLOADER_FILE}" --ondisk "$ondisk_dev" --align $bootloader_align_kb --no-table
EOF
    fi

    if ${@bb.utils.contains('DISTRO_FEATURES', 'mender-uboot', 'true', 'false', d)} && [ -n "${MENDER_UBOOT_ENV_STORAGE_DEVICE_OFFSET}" ]; then
        boot_env_align_kb=$(expr ${MENDER_UBOOT_ENV_STORAGE_DEVICE_OFFSET} / 1024)
        cat >> "$wks" <<EOF
part --source rawcopy --sourceparams="file=${WORKDIR}/uboot.env" --ondisk "$ondisk_dev" --align $boot_env_align_kb --no-table
EOF
    fi

    cat >> "$wks" <<EOF
part $boot_part_params --ondisk "$ondisk_dev" --fstype=vfat --label boot --align ${MENDER_PARTITION_ALIGNMENT_KB} --active --fixed-size ${MENDER_BOOT_PART_SIZE_MB}
part --source rootfs --ondisk "$ondisk_dev" --fstype=${ARTIFACTIMG_FSTYPE} --label primary --align ${MENDER_PARTITION_ALIGNMENT_KB} --fixed-size ${MENDER_CALC_ROOTFS_SIZE}k
part --source rootfs --ondisk "$ondisk_dev" --fstype=${ARTIFACTIMG_FSTYPE} --label secondary --align ${MENDER_PARTITION_ALIGNMENT_KB} --fixed-size ${MENDER_CALC_ROOTFS_SIZE}k
part --source rawcopy --sourceparams=file="${WORKDIR}/data.${ARTIFACTIMG_FSTYPE}" --ondisk "$ondisk_dev" --fstype=${ARTIFACTIMG_FSTYPE} --label data --align ${MENDER_PARTITION_ALIGNMENT_KB} --fixed-size ${MENDER_DATA_PART_SIZE_MB}
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
    rm -rf "$wicout/"

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
"

do_image_uefiimg[depends] += " \
    ${@d.getVarFlag('do_image_wic', 'depends', False)} \
    wic-tools:do_populate_sysroot \
    dosfstools-native:do_populate_sysroot \
    mtools-native:do_populate_sysroot \
    rsync-native:do_populate_sysroot \
    ${@bb.utils.contains('DISTRO_FEATURES', 'mender-grub', 'grub-efi:do_deploy', '', d)} \
"
do_image_sdimg[depends] += " ${@bb.utils.contains('SOC_FAMILY', 'rpi', 'bcm2835-bootfiles:do_populate_sysroot', '', d)}"

# This isn't actually a dependency, but a way to avoid sdimg and uefiimg
# building simultaneously, since wic will use the same file names in both, and
# in parallel builds this is a recipe for disaster.
IMAGE_TYPEDEP_uefiimg_append = "${@bb.utils.contains('IMAGE_FSTYPES', 'sdimg', ' sdimg', '', d)}"
