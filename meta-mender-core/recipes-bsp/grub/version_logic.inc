DEPENDS_append_mender-grub_arm = " u-boot"
DEPENDS_append_mender-grub_aarch64 = " u-boot"
RDEPENDS_${PN}_append_mender-grub_arm = " u-boot"
RDEPENDS_${PN}_append_mender-grub_aarch64 = " u-boot"

# MEN-2404: These older versions have broken EFI support. Unfortunately it does
# not seem to be possible to specify a range of conflicting versions. If so, we
# would have specified ">= 2018.11, <= 2019.07". If you are in the situation of
# having a U-Boot version older than 2018.11, you will just have to remove this
# RCONFLICT entry manually with an 'RCONFLICT_remove = "u-boot (<= 1:2019.07)"'
def mender_u_boot_version_conflict(d):
    # The version matching logic doesn't work correctly unless we match the
    # PREFERRED_PROVIDER exactly, so take that into account in this function.
    pp = d.getVar("PREFERRED_PROVIDER_u-boot")
    bad_version = "1:2019.07"

    if pp is None or pp == "" or pp == "u-boot":
        return " u-boot (<= %s)" % bad_version
    elif pp.startswith("u-boot-"):
        return " %s (<= %s)" % (pp, bad_version)
    else:
        return ""
RCONFLICTS_${PN}_mender-grub_arm = "${@mender_u_boot_version_conflict(d)}"
RCONFLICTS_${PN}_mender-grub_aarch64 = "${@mender_u_boot_version_conflict(d)}"

# It's actually U-Boot that needs the dtb files to be in the boot partition, in
# order to load EFI apps correctly, but due to the wide range of U-Boot recipes
# out there, it's easier to add the dependency here.
RDEPENDS_${PN}_append_mender-image_mender-grub_arm = " boot-partition-devicetree"
RDEPENDS_${PN}_append_mender-image_mender-grub_aarch64 = " boot-partition-devicetree"
