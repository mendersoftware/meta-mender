python() {
    if bb.utils.contains('DISTRO_FEATURES', 'mender-ubi', True, False, d):
        # Using "_defaultval" is the same as a '??=' assignment.

        d.setVarFlag("ARTIFACTIMG_FSTYPE", "_defaultval", "ubifs")

        d.setVarFlag("MENDER_STORAGE_DEVICE", "_defaultval", "ubi0")

        # The base name of the devices that hold individual volumes.
        d.setVarFlag("MENDER_STORAGE_DEVICE_BASE", "_defaultval", "${MENDER_STORAGE_DEVICE}_")

        # The numbers of the two rootfs partitions in the A/B partition layout.
        d.setVarFlag("MENDER_ROOTFS_PART_A", "_defaultval", "${MENDER_STORAGE_DEVICE_BASE}0")
        d.setVarFlag("MENDER_ROOTFS_PART_B", "_defaultval", "${MENDER_STORAGE_DEVICE_BASE}1")

        # The partition number holding the data partition.
        d.setVarFlag("MENDER_DATA_PART", "_defaultval", "${MENDER_STORAGE_DEVICE_BASE}2")
        d.setVarFlag("MENDER_DATA_PART_FSTYPE", "_defaultval", "ubifs")

        # u-boot command ubifsmount requires volume name as the only argument
        # and hence we need to keep track of that since we load kernel/dtb from
        # rootfs part
        #
        # It also needs the volume index e.g.
        # ubifsmount ubi0:rootfsa
        d.setVarFlag("MENDER_ROOTFS_PART_A_NAME", "_defaultval", "${MENDER_STORAGE_DEVICE}:rootfsa")
        d.setVarFlag("MENDER_ROOTFS_PART_B_NAME", "_defaultval", "${MENDER_STORAGE_DEVICE}:rootfsb")

        # The name of of the MTD part holding your UBI volumes.
        d.setVarFlag("MENDER_MTD_UBI_DEVICE_NAME", "_defaultval", "ubi")

        # Boot part is not used when building UBI image.
        d.setVarFlag("MENDER_BOOT_PART", "_defaultval", "")
        d.setVarFlag("MENDER_BOOT_PART_SIZE_MB", "_defaultval", "0")

        # These are not applicable when building UBI image.
        d.setVarFlag("MENDER_UBOOT_STORAGE_DEVICE", "_defaultval", "dummy")
        d.setVarFlag("MENDER_UBOOT_STORAGE_INTERFACE", "_defaultval", "dummy")
}
