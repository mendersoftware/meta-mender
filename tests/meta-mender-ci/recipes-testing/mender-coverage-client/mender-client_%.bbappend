SUMMARY = "Build a Mender client which records coverage during its invocation"

DEPENDS += "gobinarycoverage-native rsync-native"

do_instrument_client[dirs] =+ "${GOTMPDIR}"
do_instrument_client[doc] = "Modifies the Mender client source to enable coverage analysis"
do_instrument_client () {
    cd ${B}/src/${GO_IMPORT}
    bbwarn "Building the Mender client with coverage analysis"
    oe_runmake instrument-binary
}

do_configure_prepend () {
    # Remove all the src present in build if it is not a symbolic link to ${S}
    if [ -d ${B}src ]; then
        rm -rf ${B}src
    fi

}

do_configure_append () {
    # Remove the symbolic link created by go.bbclass in do_configure
    if [ -h ${B}src ]; then
        rm ${B}src
    fi
    mkdir -p ${B}src/${GO_IMPORT}
    rsync --archive --recursive --delete ${S}/src/${GO_IMPORT}/ ${B}/src/${GO_IMPORT}/
}

python () {
    # Only add coverage analysis if the client is newer than 2.2.x
    if not mender_is_2_2_or_older(d):
        # Coverage instrument the client before compiling it
        d.prependVarFlag('do_configure', 'postfuncs', "do_instrument_client ")
    else:
        bb.debug(2, "The client will not be built with coverage functionality. It is too old.")

}


# ---------------------------------------- #
#                                          #
#           Utility functions              #
#                                          #
# ---------------------------------------- #

def mender_is_2_2_or_older(d):
    # Due to some infinite recursion we can only check PV when using a non-git
    # recipe, and to detect this we check MENDER_BRANCH, which is only available
    # for Git recipes.
    version = d.getVar('MENDER_BRANCH')
    if not version:
        version = d.getVar('PV')

    return (
        version.startswith("1.")
        or version.startswith("2.0.")
        or version.startswith("2.1.")
        or version.startswith("2.2.")
    )
