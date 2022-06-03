SUMMARY:append:mender-testing-enabled = ": Build a Mender client which records coverage during its invocation"

DEPENDS:append:mender-testing-enabled = " gobinarycoverage-native"

do_instrument_client[dirs] =+ "${GOTMPDIR}"
do_instrument_client[doc] = "Modifies the Mender client source to enable coverage analysis"
do_instrument_client () {
    cd ${B}/src/${GO_IMPORT}
    bbwarn "Building the Mender client with coverage analysis"
    oe_runmake instrument-binary
}

do_instrument_client:class-native() {
    true
}

python () {
    # Only add coverage analysis if the client is newer than 2.2.x
    if bb.utils.contains("MENDER_FEATURES", "mender-testing-enabled", True, False, d):
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
