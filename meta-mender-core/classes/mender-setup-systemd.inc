# Note that a very common error with systemd is that the system hangs during the
# boot process while looking for devices. This is almost always because the
# kernel feature CONFIG_FHANDLE is not enabled.

python() {
    if mender_feature_is_enabled("mender-systemd", True, False, d) and not d.getVar("INIT_MANAGER") == "systemd":
        bb.fatal('mender-systemd is enabled in MENDER_FEATURES, but INIT_MANAGER is not set to systemd. Please make sure that either: 1) Systemd is enabled by setting INIT_MANAGER to "systemd". -or- 2) Disable mender-systemd by adding it to MENDER_FEATURES_DISABLE (may break daemon functionality).')
}
