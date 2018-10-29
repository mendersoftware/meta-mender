FILES_${PN} += "/data/etc/mender"
# Run after all mender recipes are finished.
do_install_append() {
    mkdir -p ${D}/data/etc/mender
    mv ${D}/etc/mender/mender.conf ${D}/data/etc/mender
    mv ${D}/etc/mender/server.crt ${D}/data/etc/mender
    ln -s /data/etc/mender/mender.conf ${D}/etc/mender/mender.conf
    ln -s /data/etc/mender/server.crt ${D}/etc/mender/server.crt 
}

