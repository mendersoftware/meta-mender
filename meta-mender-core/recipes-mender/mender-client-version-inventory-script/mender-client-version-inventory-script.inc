inherit mender-licensing

DESCRIPTION = "Mender Client version inventory script"
HOMEPAGE = "https://mender.io"

FILES:${PN}:append:mender-update-install = " \
    ${datadir}/mender/inventory/mender-inventory-client-version \
"

DEPENDS = "jq-native gettext-native"

S = "${WORKDIR}/git"
B = "${WORKDIR}/build"

# On production releases we must build the script using RELEASE=${PV} but for
# master and release candidates we need to tweak it.
BUILD_RELEASE ?= "${PV}"

do_compile() {
    oe_runmake \
        -C ${S} \
        $([ -n "${BUILD_RELEASE}" ] && echo RELEASE=${BUILD_RELEASE};) \
        build-inventory-script
}

do_install() {
    oe_runmake \
        -C ${S} \
        $([ -n "${BUILD_RELEASE}" ] && echo RELEASE=${BUILD_RELEASE};) \
        DESTDIR=${D} \
        prefix=${D} \
        install-inventory-script
}


################################################################################
## Dynamic generation of RCONFLICTS:
## * run_make_conflicts: The shell task runs the make target
## * actual_do_set_rconflicts: The Python function updates RCONFLICTS
## * do_set_rconflicts: The Python task that calls the function. Overridden in Git recipe

run_make_conflicts () {
    oe_runmake \
        -C ${S} \
        $([ -n "${BUILD_RELEASE}" ] && echo RELEASE=${BUILD_RELEASE};) \
        CONFLICTS_FILE=${B}/conflicts \
        generate-conflicts
}

def actual_do_set_rconflicts(d):
    bb.build.exec_func("run_make_conflicts", d)
    with open(os.path.join(d.getVar("B"), 'conflicts')) as f: conflicts_string = f.read()
    d.setVar("RCONFLICTS", conflicts_string)

python do_set_rconflicts () {
    actual_do_set_rconflicts(d)
}

addtask do_set_rconflicts after do_unpack before do_package
do_package[prefuncs] += "do_set_rconflicts"
