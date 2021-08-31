FILES_${PN}_append_mender-testing-enabled = " /data/etc/mender "
# Run after all mender recipes are finished.
do_install_append_class-target_mender-testing-enabled() {
    mkdir -p ${D}/data/etc/mender
    mv ${D}/etc/mender/mender.conf ${D}/data/etc/mender
    ln -s /data/etc/mender/mender.conf ${D}/etc/mender/mender.conf
}
