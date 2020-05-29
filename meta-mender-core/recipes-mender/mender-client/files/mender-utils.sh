#!/bin/sh

################################################################################
#
# Utility library for functions used by mender scripts
#
################################################################################

# Reads the "root" parameter passed in the kernel command line
function read_root_device() {
    [ -z "${CMDLINE+x}" ] && CMDLINE=`cat /proc/cmdline`
    for arg in ${CMDLINE}; do
        # Set optarg to option parameter, and '' if no parameter was given
        optarg=`expr "x$arg" : 'x[^=]*=\(.*\)' || echo ''`
        case $arg in
            root=*)
                echo $optarg
                ;;
        esac
    done
}
