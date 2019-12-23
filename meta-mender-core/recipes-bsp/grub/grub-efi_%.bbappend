include grub-mender.inc

FILES_${PN}_remove_mender-install = " /boot/EFI/BOOT/${GRUB_IMAGE} "
FILES_${PN}_append_mender-install = " ${MENDER_BOOT_PART_MOUNT_LOCATION}/EFI/BOOT/${GRUB_IMAGE} "

do_install_append_class-target() {
    if "${@bb.utils.contains('DISTRO_FEATURES', 'mender-install', 'true', 'false', d)}"; then
        install -d ${D}/${MENDER_BOOT_PART_MOUNT_LOCATION}
        mv ${D}/boot/EFI ${D}/${MENDER_BOOT_PART_MOUNT_LOCATION}
        rmdir ${D}/boot || true
    fi
}
