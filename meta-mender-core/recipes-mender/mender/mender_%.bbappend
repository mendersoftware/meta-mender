do_install_append_mender-systemd() {
    # Versions of Mender client after 2.2 come with the service file called
    # "mender-client" by default, but we don't want to change this in a stable
    # Yocto branch, so for warrior and older we do this rename back to the old
    # name "mender".
    if [ -e ${D}${systemd_unitdir}/system/mender-client.service ]; then
        mv ${D}${systemd_unitdir}/system/mender-client.service ${D}${systemd_unitdir}/system/mender.service
    fi
}

def mender_is_2_2_or_older(d):
    # Due to some infinite recursion we can only check PV when using a non-git
    # recipe, and to detect this we check MENDER_BRANCH, which is only available
    # for Git recipes.
    version = d.getVar('MENDER_BRANCH')
    if not version:
        version = d.getVar('PV')
    if (
        version.startswith("1.")
        or version.startswith("2.0.")
        or version.startswith("2.1.")
        or version.startswith("2.2.")
    ):
        return True
    else:
        return False

def mender_is_2_5_or_newer(d):
    # Due to some infinite recursion we can only check PV when using a non-git
    # recipe, and to detect this we check MENDER_BRANCH, which is only available
    # for Git recipes.
    version = d.getVar('MENDER_BRANCH')
    if not version:
        version = d.getVar('PV')
    if (
        version.startswith("2.5.")
        or version.startswith("2.6.")
        or version.startswith("2.7.")
        or version.startswith("2.8.")
        or version.startswith("2.9.")
        or (version.startswith("2.1") and not version.startswith("2.1."))
        or version.startswith("3.")
    ):
        return True
    else:
        return False

# This is needed for all 2.3 and later client versions, on warrior and older.
SRC_URI_append_mender-systemd = "${@' file://0001-MEN-3277-Fix-check-update-and-send-inventory-options.patch' if not mender_is_2_2_or_older(d) and not mender_is_2_5_or_newer(d) else ''}"
SRC_URI_append_mender-systemd = "${@' file://0001-MEN-3277-Fix-check-update-and-send-inventory-options-regen-2.5.0.patch' if not mender_is_2_2_or_older(d) and mender_is_2_5_or_newer(d) else ''}"
