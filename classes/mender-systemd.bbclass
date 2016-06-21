# Class to help deal with systemd and Mender.

# Suggested method for adding support for systemd, enabled by default for QEMU (vexpress-qemu.conf)
#
#DISTRO_FEATURES_append = " systemd"
#VIRTUAL-RUNTIME_init_manager = "systemd"
#DISTRO_FEATURES_BACKFILL_CONSIDERED = "sysvinit"
#VIRTUAL-RUNTIME_initscripts = ""

# Note that a very common error with systemd is that the system hangs during the
# boot process while looking for devices. This is almost always because the
# kernel feature CONFIG_FHANDLE is not enabled.

python() {
    if not bb.utils.contains('DISTRO_FEATURES', 'systemd', True, False, d):
        raise Exception("systemd is required in DISTRO_FEATURES when using mender-full or mender-systemd classes. See mender-systemd.bbclass for an example of how to enable.")
}
