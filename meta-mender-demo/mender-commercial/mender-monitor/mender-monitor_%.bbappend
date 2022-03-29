

do_install:append() {
    oe_runmake \
        -C ${S} \
        DESTDIR=${D} \
        install-example-monitors
}
