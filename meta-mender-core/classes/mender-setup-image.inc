IMAGE_FSTYPES_append = "${@bb.utils.contains('DISTRO_FEATURES', 'mender-image', ' mender', '', d)}"
IMAGE_FSTYPES_append = "${@bb.utils.contains('DISTRO_FEATURES', 'mender-image-sd', ' sdimg', '', d)}"
IMAGE_FSTYPES_append = "${@bb.utils.contains('DISTRO_FEATURES', 'mender-image-ubi', ' ubimg', '', d)}"
IMAGE_FSTYPES_append = "${@bb.utils.contains('DISTRO_FEATURES', 'mender-image-uefi', ' uefiimg', '', d)}"

MACHINE_ESSENTIAL_EXTRA_RDEPENDS_append_x86 = " kernel-image"
MACHINE_ESSENTIAL_EXTRA_RDEPENDS_append_x86-64 = " kernel-image"

python() {
    features = d.getVar('DISTRO_FEATURES').split()
    for dep in features:
        if dep.startswith("mender-image-") and 'mender-image' not in features:
            bb.fatal("If enabling %s in MENDER_FEATURES_ENABLE or DISTRO_FEATURES, mender-image must also be enabled"
                     % dep)
}

MENDER_BOOT_PART_MOUNT_LOCATION = "/uboot"
MENDER_BOOT_PART_MOUNT_LOCATION_mender-image-uefi = "/boot/efi"

# Update fstab for Mender
ROOTFS_POSTPROCESS_COMMAND_append += " mender_update_fstab_file ; "
mender_update_fstab_file() {
    if [ "${@bb.utils.contains('DISTRO_FEATURES', 'mender-image-sd', 'true', 'false', d)}" ]; then
        if [ -n "${MENDER_BOOT_PART}" ]; then
            echo "# Where the U-Boot environment resides; for devices with SD card support ONLY!" >> ${IMAGE_ROOTFS}${sysconfdir}/fstab
            mkdir -p ${IMAGE_ROOTFS}${MENDER_BOOT_PART_MOUNT_LOCATION}
            echo "${MENDER_BOOT_PART} ${MENDER_BOOT_PART_MOUNT_LOCATION} ${MENDER_BOOT_PART_FSTYPE} defaults,sync 0 0" >> ${IMAGE_ROOTFS}${sysconfdir}/fstab
        else
            bbdebug 2 "MENDER_BOOT_PART not set. Not adding to fstab..."
        fi
    fi

    mkdir -p ${IMAGE_ROOTFS}/data
    echo "${MENDER_DATA_PART}   /data                ${MENDER_DATA_PART_FSTYPE}       defaults         0  0" >> ${IMAGE_ROOTFS}${sysconfdir}/fstab
}

# Setup state script version file.
MENDER_STATE_SCRIPTS_VERSION = "2"
ROOTFS_POSTPROCESS_COMMAND_append += "${@bb.utils.contains('DISTRO_FEATURES', 'mender-image', ' mender_create_scripts_version_file ; ', '', d)}"

mender_create_scripts_version_file() {
    install -d -m 755 ${IMAGE_ROOTFS}${sysconfdir}/mender/scripts/
    echo -n "${MENDER_STATE_SCRIPTS_VERSION}" > ${IMAGE_ROOTFS}${sysconfdir}/mender/scripts/version
}
