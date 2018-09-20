# Note that a very common error with systemd is that the system hangs during the
# boot process while looking for devices. This is almost always because the
# kernel feature CONFIG_FHANDLE is not enabled.

DISTRO_FEATURES_BACKFILL_append = "${@mender_feature_is_enabled('mender-systemd', ' systemd', '', d)}"
DISTRO_FEATURES_BACKFILL_CONSIDERED_append = "${@mender_feature_is_enabled('mender-systemd', ' sysvinit', '', d)}"
VIRTUAL-RUNTIME_init_manager_mender-systemd = "systemd"
VIRTUAL-RUNTIME_initscripts_mender-systemd = ""
