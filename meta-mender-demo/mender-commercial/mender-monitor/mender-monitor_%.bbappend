
do_install_append() {
    if echo ${PV} | egrep '^1.0.'; then
        # Nothing to append on 1.0.x recipes
        true
    else
        oe_runmake \
            -C ${S} \
            DESTDIR=${D} \
            install-example-monitors
    fi
}
