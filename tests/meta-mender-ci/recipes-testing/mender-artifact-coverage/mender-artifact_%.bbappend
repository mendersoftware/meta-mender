SUMMARY:append:mender-testing-enabled = ": Build mender-artifact with coverage recording enabled"

DEPENDS:append:mender-testing-enabled = " gobinarycoverage-native rsync-native"

do_instrument_mender-artifact[dirs] =+ "${GOTMPDIR}"
do_instrument_mender-artifact[doc] = "Modifies the mender-artifact source to enable coverage analysis"
do_instrument_artifact () {
    cd ${B}/src/${GO_IMPORT}
    bbwarn "Building the mender-artifact tool with coverage analysis"
    oe_runmake instrument-binary
}

do_configure:prepend:mender-testing-enabled () {
    # Remove all the src present in build if it is not a symbolic link to ${S}
    if [ -d ${B}/src ]; then
        rm -rf ${B}/src
    fi

}

do_configure:append:mender-testing-enabled () {
    # Remove the symbolic link created by go.bbclass in do_configure
    if [ -h ${B}/src ]; then
        rm ${B}/src
    fi
    mkdir -p ${B}/src/${GO_IMPORT}
    rsync --archive --recursive --delete ${S}/src/${GO_IMPORT}/ ${B}/src/${GO_IMPORT}/
}

python () {
    if bb.utils.contains("MENDER_FEATURES", "mender-testing-enabled", True, False, d):
       if not mender_artifact_is_3_6_or_older(d):
           d.prependVarFlag('do_configure', 'postfuncs', "do_instrument_artifact ")
       else:
           bb.debug(2, "The client will not be built with coverage functionality. It is too old.")
}


# ---------------------------------------- #
#                                          #
#           Utility functions              #
#                                          #
# ---------------------------------------- #

def mender_artifact_is_3_6_or_older(d):
    # Due to some infinite recursion we can only check PV when using a non-git
    # recipe, and to detect this we check MENDER_ARTIFACT_BRANCH, which is only available
    # for Git recipes.
    version = d.getVar('MENDER_ARTIFACT_BRANCH')
    if not version:
        version = d.getVar('PV')

    return (
        version.startswith("1.")
        or version.startswith("2.")
        or version.startswith("3.1.")
        or version.startswith("3.2.")
        or version.startswith("3.3.")
        or version.startswith("3.4.")
        or version.startswith("3.5.")
        or version.startswith("3.6.")
    )
