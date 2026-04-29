# This class provides a warning when mender-client-version-inventory-script
# cannot be installed due to package conflicts
#
# When strict conflicts are enabled, the inventory script is added as RDEPENDS (default)
# When strict conflicts are disabled, the inventory script is added as RRECOMMENDS.

python mender_warn_missing_version_inventory_script() {
    if bb.utils.contains('PACKAGECONFIG', 'version-inventory-script-strict', True, False, d):
        return

    rootfs = d.getVar("IMAGE_ROOTFS")
    datadir = d.getVar("datadir")
    inventory_dir = os.path.join(rootfs + datadir, "mender/inventory")
    inventory_script = os.path.join(inventory_dir, "mender-inventory-client-version")

    if os.path.exists(inventory_dir) and not os.path.exists(inventory_script):
        bb.warn("""mender-client-version-inventory-script was NOT installed in the image.
This is likely due to a package conflict with incompatible Mender Client subcomponents.
To resolve this issue:
  1. Upgrade Mender Client subcomponents to compatible versions.
     See: https://docs.mender.io/release-information/supported-releases#mender-client
  2. Or, remove 'version-inventory-script' from PACKAGECONFIG if using custom component versions:
     PACKAGECONFIG:remove:pn-mender = "version-inventory-script\"""")
}

ROOTFS_POSTPROCESS_COMMAND += "mender_warn_missing_version_inventory_script;"
