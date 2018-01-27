# Note that a very common error with systemd is that the system hangs during the
# boot process while looking for devices. This is almost always because the
# kernel feature CONFIG_FHANDLE is not enabled.

python() {
    if bb.data.inherits_class('nativesdk', d) or bb.data.inherits_class('native', d):
        return
    if bb.utils.contains('DISTRO_FEATURES', 'mender-systemd', True, False, d) and not bb.utils.contains('DISTRO_FEATURES', 'systemd', True, False, d):
        raise Exception("systemd is required in DISTRO_FEATURES when using mender-systemd feature. See vexpress-qemu.conf for an example of how to enable.")
}
