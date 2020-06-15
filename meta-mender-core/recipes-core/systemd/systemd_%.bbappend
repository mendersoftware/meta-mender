# Avoid issues with time being out of sync on first boot.  By default,
# systemd uses its build time as the epoch. When systemd is launched
# on a system without a real time clock, this time will be detected as
# in the future and an fsck will be done.  Setting this to 0 results
# in an epoch of January 1, 1970 which is detected as an invalid time
# and the fsck will be skipped.
PACKAGECONFIG_append = "${@bb.utils.contains('DISTRO_FEATURES', 'mender-systemd', ' set-time-epoch', '', d)}"
