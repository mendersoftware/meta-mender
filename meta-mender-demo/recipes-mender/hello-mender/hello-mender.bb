DESCRIPTION = "Mender test recipe for persistent data files"
LICENSE = "Apache-2.0"

FILES_${PN} += "/data/persistent.txt"

do_compile() {
    echo 'Hello Mender config file' > hello-mender.cfg
    echo 'persistent data test' > persistent.txt
}

do_install() {
    install -d ${D}${sysconfdir}
    install -m 0644 hello-mender.cfg ${D}${sysconfdir}

    install -d ${D}/data/
    install -m 0644 persistent.txt ${D}/data/
}
