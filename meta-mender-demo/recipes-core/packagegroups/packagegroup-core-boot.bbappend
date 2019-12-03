RDEPENDS_${PN}_append = " hello-mender boot-script"

# This is for tests. Without the tests creating a special file, the service will
# do nothing.
RDEPENDS_${PN}_append_vexpress-qemu = " mender-reboot-detector"
RDEPENDS_${PN}_append_vexpress-qemu-flash = " mender-reboot-detector"
RDEPENDS_${PN}_append_qemux86-64 = " mender-reboot-detector"
RDEPENDS_${PN}_append_qemux86 = " mender-reboot-detector"

# In our demo package we use busybox, which is built in a generic, non-Yocto
# way. Therefore we need LSB support so that the dynamic linker is found.
# Specifically, this creates the symlink /lib64 -> /lib.
RDEPENDS_${PN}_append = " lsb-ld"
