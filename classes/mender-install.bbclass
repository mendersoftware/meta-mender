PREFERRED_VERSION_go_cross = "1.6%"

# Add support for systemd
#
# Note that a very common error with systemd is that the system hangs during the
# boot process while looking for devices. This is almost always because the
# kernel feature CONFIG_FHANDLE is not enabled.
DISTRO_FEATURES_append = " systemd"
VIRTUAL-RUNTIME_init_manager = "systemd"
DISTRO_FEATURES_BACKFILL_CONSIDERED = "sysvinit"
VIRTUAL-RUNTIME_initscripts = ""

IMAGE_INSTALL_append = " mender ca-certificates"
