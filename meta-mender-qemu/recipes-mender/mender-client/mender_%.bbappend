require mender-client-test-files.inc

# Remove mender-snapshot to save storage space. We are not running snapshot tests for this device
RRECOMMENDS:mender-update:remove:vexpress-qemu-flash = "mender-snapshot"
