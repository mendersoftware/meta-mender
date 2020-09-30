RDEPENDS_${PN}_append_mender-client-install = " hello-mender boot-script"

# This is for tests. Without the tests creating a special file, the service will
# do nothing.
RDEPENDS_${PN}_append_mender-client-install = "${@bb.utils.contains_any('MENDER_MACHINE', 'vexpress-qemu vexpress-qemu-flash qemux86-64 qemuxu86', ' mender-reboot-detector', '', d)}"

# In our demo package we use busybox, which is built in a generic, non-Yocto
# way. Therefore we need LSB support so that the dynamic linker is found.
# Specifically, this creates the symlink /lib64 -> /lib.
RDEPENDS_${PN}_append_mender-client-install = " lsb-ld"
