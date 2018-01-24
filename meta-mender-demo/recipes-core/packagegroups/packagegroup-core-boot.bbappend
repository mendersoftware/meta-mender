# This is for tests. Without the tests creating a special file, the service will
# do nothing.
RDEPENDS_${PN}_append_vexpress-qemu = " mender-reboot-detector"
RDEPENDS_${PN}_append_vexpress-qemu-flash = " mender-reboot-detector"
