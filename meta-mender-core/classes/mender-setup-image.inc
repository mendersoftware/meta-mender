IMAGE_FSTYPES += "${@bb.utils.contains('MENDER_FEATURES', 'mender-image', ' mender', '', d)}"
IMAGE_FSTYPES += "${@bb.utils.contains('MENDER_FEATURES', 'mender-image-sd', ' sdimg sdimg.bmap', '', d)}"
IMAGE_FSTYPES += "${@bb.utils.contains('MENDER_FEATURES', 'mender-image-ubi', ' ubimg mtdimg ubimg.bmap', '', d)}"
IMAGE_FSTYPES += "${@bb.utils.contains('MENDER_FEATURES', 'mender-image-uefi', ' uefiimg uefiimg.bmap', '', d)}"
IMAGE_FSTYPES += "${@bb.utils.contains('MENDER_FEATURES', 'mender-image-bios', ' biosimg biosimg.bmap', '', d)}"
IMAGE_FSTYPES += "${@bb.utils.contains('MENDER_FEATURES', 'mender-image-gpt', ' gptimg gptimg.bmap', '', d)}"

MACHINE_ESSENTIAL_EXTRA_RDEPENDS:append:mender-image:x86 =     " kernel-image"
MACHINE_ESSENTIAL_EXTRA_RDEPENDS:append:mender-image:x86-64 =  " kernel-image"
MACHINE_ESSENTIAL_EXTRA_RDEPENDS:append:mender-image:arm =     " \
    kernel-image \
    ${@'kernel-devicetree' if d.getVar('MENDER_EFI_LOADER').startswith('u-boot') else ''} \
"
MACHINE_ESSENTIAL_EXTRA_RDEPENDS:append:mender-image:aarch64 =     " \
    kernel-image \
    ${@'kernel-devicetree' if d.getVar('MENDER_EFI_LOADER').startswith('u-boot') else ''} \
"

python() {
    features = d.getVar('MENDER_FEATURES').split()
    for dep in features:
        if dep.startswith("mender-image-") and 'mender-image' not in features:
            bb.fatal("If enabling %s in MENDER_FEATURES_ENABLE, mender-image must also be enabled"
                     % dep)
}

MENDER_BOOT_PART_MOUNT_LOCATION = "/boot/efi"
MENDER_BOOT_PART_MOUNT_LOCATION:mender-uboot = "/uboot"
MENDER_BOOT_PART_MOUNT_LOCATION:mender-systemd-boot = "/boot"
MENDER_BOOT_PART_MOUNT_LOCATION:mender-grub:mender-bios = "/boot/grub"

# Set Yocto variable.
EFI_PREFIX:mender-image = "${MENDER_BOOT_PART_MOUNT_LOCATION}"

# Update fstab for Mender
ROOTFS_POSTPROCESS_COMMAND:append = " mender_update_fstab_file;"
mender_update_fstab_file() {
    local tmpBootPart="${MENDER_BOOT_PART}"
    local tmpDataPart="${MENDER_DATA_PART}"
    local partuuid="${@bb.utils.contains('MENDER_FEATURES', 'mender-partuuid', 'true', 'false', d)}"
    local partlabel="${@bb.utils.contains('MENDER_FEATURES', 'mender-partlabel', 'true', 'false', d)}"
    if [ ${partuuid} = "true" ]; then
        tmpBootPart="PARTUUID=${@mender_get_partuuid_from_device(d, '${MENDER_BOOT_PART}')}"
        tmpDataPart="PARTUUID=${@mender_get_partuuid_from_device(d, '${MENDER_DATA_PART}')}"
    elif [ ${partlabel} = "true" ]; then
        tmpBootPart="LABEL=${MENDER_BOOT_PART_LABEL}"
        tmpDataPart="LABEL=${MENDER_DATA_PART_LABEL}"
    fi

    if ! ${@bb.utils.contains('MENDER_FEATURES', 'mender-image-ubi', 'true', 'false', d)}; then
        if [ "${MENDER_BOOT_PART_SIZE_MB}" != "0" ] && [ -n "${MENDER_BOOT_PART}" ]; then
            echo "# Where the U-Boot environment resides; for devices with SD card support ONLY!" >> ${IMAGE_ROOTFS}${sysconfdir}/fstab
            mkdir -p ${IMAGE_ROOTFS}/${MENDER_BOOT_PART_MOUNT_LOCATION}
            printf "%-20s %-20s %-10s %-21s %-2s %s\n" ${tmpBootPart} ${MENDER_BOOT_PART_MOUNT_LOCATION} ${MENDER_BOOT_PART_FSTYPE} ${MENDER_BOOT_PART_FSTAB_OPTS} 0 2 >> ${IMAGE_ROOTFS}${sysconfdir}/fstab
        else
            bbdebug 2 "MENDER_BOOT_PART not applicable. Not adding to fstab..."
        fi
    fi

    mkdir -p ${IMAGE_ROOTFS}/data
    printf "%-20s %-20s %-10s %-21s %-2s %s\n" ${tmpDataPart} /data ${MENDER_DATA_PART_FSTYPE} ${MENDER_DATA_PART_FSTAB_OPTS} 0 2 >> ${IMAGE_ROOTFS}${sysconfdir}/fstab

    if [ -n "${MENDER_EXTRA_PARTS}" ]; then
        local extra_part_fstab="${@get_extra_parts_fstab(d)}"
        local mounts="${@get_extra_parts_mount_locations(d)}"
        for mount in ${mounts}; do
            mkdir -p ${IMAGE_ROOTFS}/${mount}
        done

        parts="${extra_part_fstab}"
        printf "%-20s %-20s %-10s %-21s %-2s %s\n" $parts >> ${IMAGE_ROOTFS}${sysconfdir}/fstab
    fi

    if [ "${MENDER_SWAP_PART_SIZE_MB}" -ne "0" ]; then
        local swap_part_num="${@mender_get_swap_part_num(d)}"
	if ${@bb.utils.contains('MENDER_FEATURES', 'mender-partuuid', 'true', 'false', d)}; then
	    swap_uuid="${@d.getVar('MENDER_SWAP_PART_UUID')}"
            printf "%-20s %-20s %-10s %-21s %-2s %s\n"  "PARTUUID=${swap_uuid}" swap swap defaults 0  0 >> ${IMAGE_ROOTFS}${sysconfdir}/fstab
	else
            printf "%-20s %-20s %-10s %-21s %-2s %s\n"  ${MENDER_STORAGE_DEVICE_BASE}${swap_part_num} swap swap defaults 0  0 >> ${IMAGE_ROOTFS}${sysconfdir}/fstab
	fi
    fi
}

def mender_default_state_scripts_version(d):
    pref_mender = d.getVar('PREFERRED_VERSION:pn-mender-client')
    if pref_mender and pref_mender.startswith("1."):
        return "2"
    else:
        return "3"

# Setup state script version file.
MENDER_STATE_SCRIPTS_VERSION = "${@mender_default_state_scripts_version(d)}"
ROOTFS_POSTPROCESS_COMMAND:append = "${@bb.utils.contains('MENDER_FEATURES', 'mender-image', ' mender_create_scripts_version_file;', '', d)}"

mender_create_scripts_version_file() {
    install -d -m 755 ${IMAGE_ROOTFS}${sysconfdir}/mender/scripts/
    echo -n "${MENDER_STATE_SCRIPTS_VERSION}" > ${IMAGE_ROOTFS}${sysconfdir}/mender/scripts/version
}

IMAGE_ROOTFS_EXCLUDE_PATH:append:mender-image = " data/ ${@d.getVar('MENDER_BOOT_PART_MOUNT_LOCATION')[1:]}/"


################################################################################
# Implementation of IMAGE_ROOTFS_EXCLUDE_PATH
################################################################################

python prepare_excluded_directories() {
    exclude_var = d.getVar('IMAGE_ROOTFS_EXCLUDE_PATH')
    if not exclude_var:
        return

    taskname = d.getVar("BB_CURRENTTASK")

    if d.getVarFlag('do_%s' % taskname, 'respect_exclude_path') == '0':
        bb.debug(1, "'IMAGE_ROOTFS_EXCLUDE_PATH' is set but 'respect_exclude_path' variable flag is 0 for this image type, so ignoring it")
        return

    import subprocess
    from oe.path import copyhardlinktree

    exclude_list = exclude_var.split()

    rootfs_orig = d.getVar('IMAGE_ROOTFS')
    # We need a new rootfs directory we can delete files from. Copy to
    # workdir.
    new_rootfs = os.path.realpath(os.path.join(d.getVar("WORKDIR"), "rootfs.%s" % taskname))

    if os.path.lexists(new_rootfs):
        subprocess.check_call(["rm", "-rf", new_rootfs])

    copyhardlinktree(rootfs_orig, new_rootfs)

    for orig_path in exclude_list:
        path = orig_path
        if os.path.isabs(path):
            bb.fatal("IMAGE_ROOTFS_EXCLUDE_PATH: Must be relative: %s" % orig_path)

        full_path = os.path.realpath(os.path.join(new_rootfs, path))

        # Disallow climbing outside of parent directory using '..',
        # because doing so could be quite disastrous (we will delete the
        # directory).
        if not full_path.startswith(new_rootfs):
            bb.fatal("'%s' points to a path outside the rootfs" % orig_path)

        if not os.path.lexists(full_path):
            # Nothing to do if it doesn't exist.
            continue

        if path.endswith(os.sep):
            # Delete content only.
            for entry in os.listdir(full_path):
                full_entry = os.path.join(full_path, entry)
                if os.path.isdir(full_entry) and not os.path.islink(full_entry):
                    subprocess.check_call(["rm", "-rf", full_entry])
                else:
                    subprocess.check_call(["rm", "-f", full_entry])
        else:
            # Delete whole directory.
            subprocess.check_call(["rm", "-rf", full_path])

    # Save old value for cleanup later.
    d.setVar('IMAGE_ROOTFS_ORIG', rootfs_orig)
    d.setVar('IMAGE_ROOTFS', new_rootfs)
}

python cleanup_excluded_directories() {
    exclude_var = d.getVar('IMAGE_ROOTFS_EXCLUDE_PATH')
    if not exclude_var:
        return

    import subprocess

    taskname = d.getVar("BB_CURRENTTASK")

    if d.getVarFlag('do_%s' % taskname, 'respect_exclude_path') == '0':
        return

    import shutil

    rootfs_dirs_excluded = d.getVar('IMAGE_ROOTFS')
    rootfs_orig = d.getVar('IMAGE_ROOTFS_ORIG')
    # This should never happen, since we should have set it to a different
    # directory in the prepare function.
    assert rootfs_dirs_excluded != rootfs_orig

    subprocess.check_call(["rm", "-rf", rootfs_dirs_excluded])
    d.setVar('IMAGE_ROOTFS', rootfs_orig)
}

python() {
    if not bb.data.inherits_class("image", d):
        return

    d.appendVarFlag("do_rootfs", "vardeps", " IMAGE_ROOTFS_EXCLUDE_PATH")

    fstypes = d.getVar('IMAGE_FSTYPES') + " " + d.getVar("ARTIFACTIMG_FSTYPE")
    handled = set()

    for image_type in fstypes.split():
        image_name, image_extension = os.path.splitext(image_type)
        if image_extension:
            image_type = image_name

        if image_type in handled:
            continue

        task = "do_image_%s" % image_type
        d.appendVarFlag(task, "prefuncs", " prepare_excluded_directories")
        d.appendVarFlag(task, "postfuncs", " cleanup_excluded_directories")

        handled.add(image_type)
}
