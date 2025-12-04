inherit mender-licensing

DESCRIPTION = "Mender Client version inventory script"
HOMEPAGE = "https://mender.io"

FILES:${PN}:append:mender-update-install = " \
    ${datadir}/mender/inventory/mender-inventory-client-version \
"

DEPENDS = "jq-native gettext-native"

S = "${WORKDIR}/git"
B = "${WORKDIR}/build"

do_compile() {
    oe_runmake \
        -C ${S} \
        RELEASE=${PV} \
        build-inventory-script
}

do_install() {
    oe_runmake \
        -C ${S} \
        RELEASE=${PV} \
        DESTDIR=${D} \
        prefix=${D} \
        install-inventory-script
}


################################################################################
## Dynamic generation of RCONFLICTS:
## * The shell task runs the make target
## * The Python task updates RCONFLICTS for do_package

run_make_conflicts () {
    oe_runmake \
        -C ${S} \
        RELEASE=${PV} \
        CONFLICTS_FILE=${B}/conflicts \
        generate-conflicts
}

python do_set_rconflicts () {
    bb.build.exec_func("run_make_conflicts", d)
    with open(os.path.join(d.getVar("B"), 'conflicts')) as f: conflicts_string = f.read()
    d.setVar("RCONFLICTS", conflicts_string)
}

addtask do_set_rconflicts after do_unpack before do_package
do_package[prefuncs] += "do_set_rconflicts"
