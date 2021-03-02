RDEPENDS_${PN}_append_mender-client-install = " hello-mender boot-script"

# This is for tests. Without the tests creating a special file, the service will
# do nothing.
RDEPENDS_${PN}_append_mender-client-install = "${@bb.utils.contains_any('MENDER_MACHINE', 'vexpress-qemu vexpress-qemu-flash qemux86-64 qemuxu86', ' mender-reboot-detector', '', d)}"

# In our demo package we use busybox, which is built in a generic, non-Yocto
# way. Therefore we need LSB support so that the dynamic linker is found.
# Specifically, this creates the symlink /lib64 -> /lib.
RDEPENDS_${PN}_append_mender-client-install = " lsb-ld"

def maybe_mender_connect(d):
    pref = d.getVar('PREFERRED_VERSION_pn-mender-client')
    if pref is None:
        return " mender-connect"

    if pref[0:3] in ["1.7", "2.0", "2.1", "2.2", "2.3", "2.4"]:
        return ""
    else:
        return " mender-connect"

def maybe_mender_configure(d):
    pref = d.getVar('PREFERRED_VERSION_pn-mender-client')
    if pref is None:
        return " mender-configure mender-configure-demo mender-configure-scripts"

    if pref[0:3] in ["1.7", "2.0", "2.1", "2.2", "2.3", "2.4", "2.5"]:
        return ""
    else:
        return " mender-configure mender-configure-demo mender-configure-scripts"

# Install Mender add-ons, but only if the client is recent enough.
RDEPENDS_${PN}_append_mender-image = "${@maybe_mender_connect(d)}${@maybe_mender_configure(d)}"
