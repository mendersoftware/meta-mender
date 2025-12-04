# See MEN-8977
python do_maybe_print_warning_major_upgrade() {
    if not (d.getVar("PREFERRED_VERSION_mender") or d.getVar("PREFERRED_VERSION")):
        bb.warn("PREFERRED_VERSION is empty. The default mender version changed to an actively supported one (4.x to 5.x). Please verify all functionality, specifically custom scripting. For staying with the EOL version use 'PREFERRED_VERSION_mender = \"4.0.7\"'")
        bb.warn("Changes in major version:  https://docs.mender.io/client-installation/install-with-debian-package/upgrading#upgrade-the-mender-client-4-x-series-to-5-x-series")
}

addtask do_maybe_print_warning_major_upgrade after do_fetch before do_install
