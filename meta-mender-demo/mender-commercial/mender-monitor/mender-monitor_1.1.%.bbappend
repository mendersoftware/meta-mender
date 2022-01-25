

do_install_append() {
    oe_runmake \
        -C ${S} \
        DESTDIR=${D} \
        install-example-monitors
}
