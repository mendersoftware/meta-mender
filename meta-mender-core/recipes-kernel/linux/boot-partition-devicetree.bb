# A recipe which installs all the DTB files from KERNEL_DEVICETREE into the
# "dtb" folder of the boot partition.

LICENSE = "GPL-2.0"

FILES_${PN} = " ${MENDER_BOOT_PART_MOUNT_LOCATION}/dtb"

DEPENDS = "virtual/kernel"

do_install() {
    install -d -m 755 ${D}/${MENDER_BOOT_PART_MOUNT_LOCATION}/dtb

    for dtb_path in ${KERNEL_DEVICETREE}; do
        install -m 0644 ${DEPLOY_DIR_IMAGE}/$(basename $dtb_path) ${D}/${MENDER_BOOT_PART_MOUNT_LOCATION}/dtb/
    done
}
do_install[depends] = "virtual/kernel:do_deploy"
