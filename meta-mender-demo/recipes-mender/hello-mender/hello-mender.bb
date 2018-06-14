DESCRIPTION = "Mender test recipe for persistent data files"
LICENSE = "Apache-2.0"

inherit deploy

do_compile() {
    echo 'Hello Mender config file' > hello-mender.cfg
    echo 'persistent data test' > persistent.txt
}

do_install() {
    install -d ${D}${sysconfdir}
    install -m 0644 hello-mender.cfg ${D}${sysconfdir}
}

do_deploy() {
    install -d ${DEPLOYDIR}/persist
    install -m 0644 persistent.txt ${DEPLOYDIR}/persist
}
addtask do_deploy after do_compile before do_build
