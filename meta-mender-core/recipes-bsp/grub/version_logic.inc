DEPENDS:append_mender-grub:arm = " u-boot"
DEPENDS:append_mender-grub:aarch64 = " u-boot"
RDEPENDS:${PN}:append_mender-grub:arm = " u-boot"
RDEPENDS:${PN}:append_mender-grub:aarch64 = " u-boot"

# MEN-2404: These older versions have broken EFI support. Unfortunately it does
# not seem to be possible to specify a range of conflicting versions. If so, we
# would have specified ">= 2018.11, <= 2019.07". If you are in the situation of
# having a U-Boot version older than 2018.11, you will just have to remove this
# RCONFLICT entry manually with an 'RCONFLICT:remove = "u-boot (<= 1:2019.07)"'
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
RCONFLICTS:${PN}_mender-grub:arm = "${@mender_u_boot_version_conflict(d)}"
RCONFLICTS:${PN}_mender-grub:aarch64 = "${@mender_u_boot_version_conflict(d)}"

# It's actually U-Boot that needs the dtb files to be in the boot partition, in
# order to load EFI apps correctly, but due to the wide range of U-Boot recipes
# out there, it's easier to add the dependency here.
RDEPENDS:${PN}:append_mender-image_mender-grub:arm = " boot-partition-devicetree"
RDEPENDS:${PN}:append_mender-image_mender-grub:aarch64 = " boot-partition-devicetree"
