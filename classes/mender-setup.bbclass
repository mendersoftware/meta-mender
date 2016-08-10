# ------------------------------ CONFIGURATION ---------------------------------

# The storage device that holds the device partitions.
MENDER_STORAGE_DEVICE ?= "/dev/mmcblk0"

# The interface to load partitions from. This is normally empty, in which case
# it is deduced from MENDER_STORAGE_DEVICE. Only use this if the interface
# cannot be deduced from MENDER_STORAGE_DEVICE.
MENDER_UBOOT_STORAGE_INTERFACE ?= ""

# The device number of the interface to load partitions from. This is normally
# empty, in which case it is deduced from MENDER_STORAGE_DEVICE. Only use this
# if the indexing of devices is different in U-Boot and in the Linux kernel.
MENDER_UBOOT_STORAGE_DEVICE ?= ""

# The base name of the devices that hold individual partitions.
# This is often MENDER_STORAGE_DEVICE + "p".
MENDER_STORAGE_DEVICE_BASE ?= "/dev/mmcblk0p"

# The partition number holding the boot partition.
MENDER_BOOT_PART ?= "${MENDER_STORAGE_DEVICE_BASE}1"

# The numbers of the two rootfs partitions in the A/B partition layout.
MENDER_ROOTFS_PART_A ?= "${MENDER_STORAGE_DEVICE_BASE}2"
MENDER_ROOTFS_PART_B ?= "${MENDER_STORAGE_DEVICE_BASE}3"

# The partition number holding the data partition.
MENDER_DATA_PART ?= "${MENDER_STORAGE_DEVICE_BASE}5"

# --------------------------- END OF CONFIGURATION -----------------------------


################################################################################
################################################################################


DISTRO_FEATURES_BACKFILL_append = " \
                                   mender-uboot \
                                   mender-image \
                                   mender-service"


# --------------------------- MENDER CLIENT SECTION ----------------------------

PREFERRED_VERSION_go_cross = "1.6%"

IMAGE_INSTALL_append = " mender ca-certificates"

# ------------------------ END OF MENDER CLIENT SECTION ------------------------


# ------------------------- SERVICE RELATED SECTION ----------------------------

# Suggested method for adding support for systemd, enabled by default for QEMU.
#
#DISTRO_FEATURES_append = " systemd"
#VIRTUAL-RUNTIME_init_manager = "systemd"
#DISTRO_FEATURES_BACKFILL_CONSIDERED = "sysvinit"
#VIRTUAL-RUNTIME_initscripts = ""
DISTRO_FEATURES_append_vexpress-qemu = " systemd"
VIRTUAL-RUNTIME_init_manager_vexpress-qemu = "systemd"
DISTRO_FEATURES_BACKFILL_CONSIDERED_vexpress-qemu = "sysvinit"
VIRTUAL-RUNTIME_initscripts_vexpress-qemu = ""

# Note that a very common error with systemd is that the system hangs during the
# boot process while looking for devices. This is almost always because the
# kernel feature CONFIG_FHANDLE is not enabled.

python() {
    if d.getVar('MACHINE', False) != 'vexpress-qemu' and bb.utils.contains('DISTRO_FEATURES', 'mender-service', True, False, d) and not bb.utils.contains('DISTRO_FEATURES', 'systemd', True, False, d):
        raise Exception("systemd is required in DISTRO_FEATURES when mender-service is in DISTRO_FEATURES. See mender-setup.bbclass for an example of how to enable, or disable the mender-service feature.")
}

# ---------------------- END OF SERVICE RELATED SECTION ------------------------


# -------------------------- IMAGE RELATED SECTION -----------------------------

# IMAGE_CLASSES for some reason cannot be defined inside of a python() block.
IMAGE_CLASSES_append = " ${@bb.utils.contains('DISTRO_FEATURES', 'mender-image', 'mender-sdimg', '', d)}"

python() {
    if not bb.utils.contains('DISTRO_FEATURES', 'mender-image', True, False, d):
        return

    #Make sure we are creating sdimg with all needed partitioning.
    d.setVar('IMAGE_FSTYPES_append', ' sdimg')
}

# ----------------------- END OF IMAGE RELATED SECTION -------------------------


# -------------------------- UBOOT RELATED SECTION -----------------------------

python() {
    if not bb.utils.contains('DISTRO_FEATURES', 'mender-uboot', True, False, d):
        return

    if not d.getVar('IMAGE_BOOT_ENV_FILE', False):
        d.setVar('IMAGE_BOOT_ENV_FILE', 'uboot.env')

    d.setVar('IMAGE_BOOT_FILES_append', " " + d.getVar('IMAGE_BOOT_ENV_FILE', ""))
    d.setVar('EXTRA_IMAGEDEPENDS_append', ' u-boot')
    d.setVar('RDEPENDS_mender_append', ' u-boot u-boot-fw-utils')
}

# ----------------------- END OF UBOOT RELATED SECTION -------------------------
