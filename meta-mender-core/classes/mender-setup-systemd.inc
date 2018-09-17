# Note that a very common error with systemd is that the system hangs during the
# boot process while looking for devices. This is almost always because the
# kernel feature CONFIG_FHANDLE is not enabled.

DISTRO_FEATURES_append = " ${@bb.utils.contains('MENDER_FEATURES_ENABLE', 'mender-systemd', 'systemd', '', d)}"
DISTRO_FEATURES_BACKFILL_CONSIDERED = "${@bb.utils.contains('MENDER_FEATURES_ENABLE', 'mender-systemd', 'sysvinit', '', d)}"
VIRTUAL-RUNTIME_init_manager_mender-systemd = "systemd"
VIRTUAL-RUNTIME_initscripts_mender-systemd = ""
