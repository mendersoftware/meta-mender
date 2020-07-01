#!/bin/bash

UBI=0

SCRIPT_DIR="$(readlink -f "$(dirname "$0")")"

if [ -z "$1" ] || [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    echo "This script should not be run on its own. Use uboot_auto_configure.sh."
    exit 1
fi

set -e

get_candidate_list() {
    # Search for all files that are relative paths, and do not start with what
    # looks like an option flag (-I), and return the list.
    for file in $(egrep -io '(^| )([a-z0-9][-.a-z0-9_/]*)?include[-.a-z0-9_/]*' "$DEP_FILE"); do
        if [ ! -f "$file" ]; then
            continue
        fi

        # Don't change env_default.h or any mender file, we have those under
        # control.
        bname="$(basename "$file")"
        if [ "$bname" = env_default.h ] || grep -q 'mender' <<<"$bname"; then
            continue
        fi

        echo "$file"
    done
}

patch_candidate_list() {
    # Execute supplied sed command on whole candidate list.
    for file in $(get_candidate_list); do
        sed -i -rne "$1" "$file"
    done
}

definition_for_kconfig_files() {
    if [ -n "${2:-}" ]; then
        echo "$1=$2"
    elif [ -n "${1:-}" ]; then
        echo "$1=y"
    else
        echo ""
    fi
}

replace_definition() {
    # Replaces definitions in source files, taking into account that it may span
    # multiple lines using '\'.
    # If the function is given only one argument, it deletes/disables the
    # definition, if given two, it replaces it with that definition, if given
    # three, it gives the new definition that value.

    patch_candidate_list "\\%^[ \t]*#[ \t]*define[ \t]*$1\\b% {:start; /\\\\\$/ {n; b start; }; b; }; p"

    # Also patch defconfig file:
    # 1. Remove existing occurrences.
    sed -i -re "\\%^$1=.*%d" configs/$CONFIG
    # 2. Add disables for all matching keys we can find
    local keys="$(find -name Kconfig | xargs sed -rne "\\%^config +(${1#CONFIG_}) *$% {s%^config +(${1#CONFIG_}) *$%CONFIG_\\1%; p}")"
    for key in $keys; do
        # Disable keys that aren't already disabled.
        if ! grep -q "^# *$key  *is not set *\$" configs/$CONFIG; then
            echo "# $key is not set" >> configs/$CONFIG
        fi
    done

    # Add definition.
    if [ -n "${2:-}" ]; then
        shift
        add_definition "$@"
    fi
}

add_definition() {
    # Adds a definition in the most appropriate place, if it doesn't exist.

    kconfig_repl="$(definition_for_kconfig_files "$@")"

    if is_kconfig_option "$1"; then
        # Skip adding if it already exists.
        if fgrep -q "$kconfig_repl" configs/$CONFIG; then
            return 0
        fi

        # Remove disabling lines, if there are any.
        egrep -v "^# *$1 is not set *$" configs/$CONFIG > configs/$CONFIG.tmp
        mv -f configs/$CONFIG.tmp configs/$CONFIG

        # In the Kconfig case it's easy, just add it to the defconfig file.
        python3 $SCRIPT_DIR/add_kconfig_option_with_depends.py --src-dir=. --defconfig-file=configs/$CONFIG "$kconfig_repl"
    else
        # In the pre-Kconfig case, it's more open. We need to add it somewhere
        # in the source, but it's not obvious where. Add it to
        # config_defaults.h.
        echo "#define $1${2:+ $2}" >> include/config_defaults.h
    fi

    if ! definition_exists "$1"; then
        # If it STILL doesn't exist, then we failed to add it and the patching
        # failed.
        echo "Unable to add definition $1. Patching failed."
        return 1
    fi
}

append_to_definition() {
    # Appends something to a string definition.

    if ! definition_exists "$1"; then
        echo "Tried to append to definition $1, but it doesn't exist!" 1>&2
        exit 1
    fi

    if is_kconfig_option "$1"; then
        sed -re "s%^$1=(.*)\"%$1=\1$2\"%" configs/$CONFIG
    else
        # Add it to the last non-backslash-continued line.
        patch_candidate_list "\\%^[ \t]*#[ \t]*define[ \t]*$1\\b% {:start; /\\\\$/ {p; n; b start}; s%\$% $2%}; p"
    fi
}

definition_exists() {
    # Returns 0 if the definition is found either in the source code or in the
    # config definition.

    any_success=1
    for file in $(get_candidate_list); do
        egrep -q "^[ \t]*#[ \t]*define[ \t]*$1\\b" "$file" && any_success=0 && break
    done
    egrep -q "(^$1=.*)|(^# *$1  *is not set *\$)" configs/$CONFIG && any_success=0
    return $any_success
}

is_kconfig_option() {
    # Returns whether a config option appears to be a Kconfig option or not.

    # Doing this checking is really tricky though. We can't look in Kconfig
    # files because they have if-statements that mean we can easily misdetect
    # that something is supported when it really isn't. We also cannot look
    # directly in .config, because other options that the option we're trying to
    # add depends on, may hide the option as well.
    #
    # So what we do is this: We use the temporary build directory, make a copy
    # of the _defconfig file, and then use the
    # add_kconfig_option_with_depends.py tool to try to add the option with all
    # its dependencies. Then we check .config file for the presence of the
    # option, since all of the option's dependencies should have been resolved
    # now, and the Kconfig if-statements also respected. If the option still
    # isn't there, then we conclude it is not a Kconfig option.

    # Special case for CONFIG_BOOTCOUNT_ENV: Due to conditional selection, ENV
    # may be missing from the .config file. However, it is in Kconfig if
    # CONFIG_BOOTCOUNT_LIMIT is.
    if [ "$1" = "CONFIG_BOOTCOUNT_ENV" ]; then
        is_kconfig_option CONFIG_BOOTCOUNT_LIMIT || return $?
        return $?
    fi

    cp $BUILD_DIR/configs/$CONFIG $BUILD_DIR/configs/$CONFIG.backup
    python3 $SCRIPT_DIR/add_kconfig_option_with_depends.py --src-dir=$BUILD_DIR --defconfig-file=$BUILD_DIR/configs/$CONFIG "$kconfig_repl"

    # Update .config
    make HOSTCC="$HOSTCC" CC="$CC" -C $BUILD_DIR $CONFIG

    # Check .config file for such the option.
    if egrep -q "^($1=|# $1 is not set)" "$BUILD_DIR/.config"; then
        ret=0
    else
        ret=1
    fi

    mv $BUILD_DIR/configs/$CONFIG.backup $BUILD_DIR/configs/$CONFIG

    return $ret
}

remove_bootvar() {
    # Removes boot variables of the form "var=" in the various U-Boot source
    # files. It makes sure to remove multiline definitions, everything up to the
    # next '\0'. If the line does not end with a backslash, it will also leave a
    # blank line in case the previous line does.

    patch_candidate_list "/\\b$1=/ {:start; /\\\\0/ {/\\\\\$/ b; s/.*//; p; b;}; n; b start; }; p;"
}

rename_bootvar() {
    # Renames boot variables of the form "var=" in the various U-Boot source
    # files.

    patch_candidate_list "s/\\b$1=/$2=/; p"
}

extract_addr() {
    for candidate in $ADDR_CANDIDATES; do
        if egrep -q "^$candidate=" "$COMPILED_ENV"; then
            echo "$candidate"
            return 0
        fi
    done
    return 1
}

extract_kernel_addr() {
    # Ordered list of all address formats we try, we will use the first one we
    # find. This was assembled by looking at the frequency of occurrences of
    # various address variables in stock U-Boot.
    ADDR_CANDIDATES="
kernel_addr_r
kernel_addr
kernel_addr_load
kerneladdr
kernaddr
memaddrlinux
loadaddr
load_addr
load_addr_r
"
    if ! extract_addr "$ADDR_CANDIDATES"; then
        return 1
    fi
}

extract_fdt_addr() {
    # Ordered list of all address formats we try, we will use the first one we
    # find. This was assembled by looking at the frequency of occurrences of
    # various address variables in stock U-Boot.
    ADDR_CANDIDATES="
fdt_addr_r
fdt_addr
fdtaddr
dtbaddr
memaddrdtb
dtbloadaddr
dtb_addr
"
    if ! extract_addr "$ADDR_CANDIDATES"; then
        echo "Could not find fdt/dtb load address!" 1>&2
        return 1
    fi
}

patch_all_candidates() {
    # This is the main function of the file, and carries out all the sub
    # functions for patching U-Boot.

    # If this file contains a bootcmd definition, remove it.
    remove_bootvar \
        "bootcmd"

    replace_definition \
        'CONFIG_ENV_SIZE' \
        'CONFIG_ENV_SIZE' \
        "$CONFIG_ENV_SIZE"

    # Remove this entry.
    replace_definition \
        'CONFIG_ENV_RANGE'

    if [ $UBI = 1 ]; then
        patch_all_candidates_ubi
    else
        patch_all_candidates_sdimg
    fi

    # There are so many variants of CONFIG_BOOTCOUNT, just remove all of them.
    # And then make sure our definitions are added.
    replace_definition \
        'CONFIG_BOOTCOUNT_[^ ]*' \
        'CONFIG_BOOTCOUNT_LIMIT'
    add_definition \
        'CONFIG_BOOTCOUNT_ENV'

    # Patch away "root=/dev/blah" arguments, we will provide our own. Take care
    # to replace an occurrence ending in '\0' first, to avoid losing it if
    # present.
    patch_candidate_list \
        '\%bootargs=|setenv *bootargs% {:start;s%\broot=[^ "]*\\0( |(")|$)%\\0\2%g; s%\broot=[^ "]*( |(")|$)%\2%g; p; /\\0/ b; n; b start; }; p;'
    sed -i -re '/^CONFIG_BOOTARGS=/ s/\broot=[^ "]* *//' configs/$CONFIG

    # Find load address for FDT/DTB file and make sure it's in fdt_addr_r.
    if fdt_addr="$(extract_fdt_addr)"; then
        if [ "$fdt_addr" != "fdt_addr_r" ]; then
            remove_bootvar \
                "fdt_addr_r"
        fi
        rename_bootvar \
            "$fdt_addr" \
            "fdt_addr_r"
    fi

    # Find load address for kernel and make sure it's in kernel_addr_r.
    if kernel_addr="$(extract_kernel_addr)"; then
        if [ "$kernel_addr" != "kernel_addr_r" ]; then
            remove_bootvar \
                "kernel_addr_r"
        fi
        rename_bootvar \
            "$kernel_addr" \
            "kernel_addr_r"
    else
        # Alright, no dedicated address. Let's try the second best, find it by
        # looking at existing boot commands.
        addr=$(sed -nre '/boot[miz] *(0x[0-9a-fA-F]+)/ {s/.*boot[miz] *(0x[0-9a-fA-F]+).*/\1/; p}' "$COMPILED_ENV" | head -n1)

        # Using the :- syntax is because "set -u" is in effect.
        if [ -n "${addr:-}" ]; then
            if definition_exists "CONFIG_EXTRA_ENV_SETTINGS"; then
                append_to_definition "CONFIG_EXTRA_ENV_SETTINGS" "\"kernel_addr_r=$addr\\\\0\""
            else
                add_definition "CONFIG_EXTRA_ENV_SETTINGS" "\"kernel_addr_r=$addr\\\\0\""
            fi
        else
            echo "Could not find kernel load address!" 1>&2
            echo "This is the obtained environment:"
            cat "$COMPILED_ENV"
            # Continue without, some boot commands don't use addresses at all.
        fi
    fi

    # If this file contains a CONFIG_BOOTCOMMAND definition, remove everything
    # from it up to the next line not ending with '\'. This is actually an
    # unnecessary step, since CONFIG_MENDER_BOOTCOMMAND is the one that will be
    # used, but it makes it clearer what the patch is trying to do, if anybody
    # needs to look at the end result and/or tweak it.
    replace_definition \
        'CONFIG_BOOTCOMMAND'
}

patch_all_candidates_sdimg() {
    replace_definition \
        'CONFIG_ENV_OFFSET' \
        'CONFIG_ENV_OFFSET' \
        "$CONFIG_ENV_OFFSET"
    replace_definition \
        'CONFIG_ENV_OFFSET_REDUND' \
        'CONFIG_ENV_OFFSET_REDUND' \
        "$CONFIG_ENV_OFFSET_REDUND"
    replace_definition \
        'CONFIG_SYS_REDUNDAND_ENVIRONMENT' \
        'CONFIG_SYS_REDUNDAND_ENVIRONMENT'

    # Remove all of the below entries.
    replace_definition \
        'CONFIG_SYS_MMC_ENV_DEV' \
        'CONFIG_SYS_MMC_ENV_DEV' \
        "$CONFIG_SYS_MMC_ENV_DEV"
    replace_definition \
        'CONFIG_SYS_MMC_ENV_PART' \
        'CONFIG_SYS_MMC_ENV_PART' \
        "$CONFIG_SYS_MMC_ENV_PART"

    # Make sure the environment is in MMC.
    replace_definition \
        'CONFIG_ENV_IS_(NOWHERE|IN_[^ ]*)' \
        'CONFIG_ENV_IS_IN_MMC'

    add_definition \
        'CONFIG_CMD_EXT4'
    add_definition \
        'CONFIG_CMD_FS_GENERIC'
    add_definition \
        'CONFIG_MMC'
}

patch_all_candidates_ubi() {
    # This was the old way to refer to CONFIG_MTDIDS_DEFAULT and
    # CONFIG_MTDPARTS_DEFAULT, without the "CONFIG_" prefix. Alias them to the
    # new ones.
    replace_definition \
        'MTDIDS_DEFAULT' \
        'MTDIDS_DEFAULT' \
        'CONFIG_MTDIDS_DEFAULT'
    replace_definition \
        'MTDPARTS_DEFAULT' \
        'MTDPARTS_DEFAULT' \
        'CONFIG_MTDPARTS_DEFAULT'

    replace_definition \
        'CONFIG_MTDIDS_DEFAULT' \
        'CONFIG_MTDIDS_DEFAULT' \
        "$CONFIG_MTDIDS_DEFAULT"
    replace_definition \
        'CONFIG_MTDPARTS_DEFAULT' \
        'CONFIG_MTDPARTS_DEFAULT' \
        "$CONFIG_MTDPARTS_DEFAULT"

    # Make sure the environment is in Flash.
    replace_definition \
        'CONFIG_ENV_IS_(NOWHERE|IN_[^ ]*)' \
        'CONFIG_ENV_IS_IN_UBI'

    replace_definition \
        'CONFIG_SYS_REDUNDAND_ENVIRONMENT' \
        'CONFIG_SYS_REDUNDAND_ENVIRONMENT'

    # And remove volume definitions of environment so Mender can configure them.
    replace_definition \
        'CONFIG_ENV_UBI_PART' \
        'CONFIG_ENV_UBI_PART' \
        "$CONFIG_ENV_UBI_PART"
    replace_definition \
        'CONFIG_ENV_UBI_VOLUME' \
        'CONFIG_ENV_UBI_VOLUME' \
        "$CONFIG_ENV_UBI_VOLUME"
    replace_definition \
        'CONFIG_ENV_UBI_VOLUME_REDUND' \
        'CONFIG_ENV_UBI_VOLUME_REDUND' \
        "$CONFIG_ENV_UBI_VOLUME_REDUND"

    add_definition \
        'CONFIG_CMD_MTDPARTS'
    add_definition \
        'CONFIG_CMD_UBI'
    add_definition \
        'CONFIG_CMD_UBIFS'

    if is_kconfig_option "CONFIG_MTD"; then
        add_definition \
            'CONFIG_MTD'
    else
        add_definition \
            'CONFIG_MTD_DEVICE'
    fi

    add_definition \
        'CONFIG_MTD_PARTITIONS'
}

if [ "$1" = "--patch-config-file" ]; then
    if [ $# -gt 1 ]; then
        echo "--patch-config-file should be first and only argument."
        exit 1
    fi
    # Patch config file to use a local one instead of absolute path. This means
    # we can use the env tools for probing during the build preparations.
    sed -i -e 's/^[ \t]*#[ \t]*define[ \t]*CONFIG_FILE\b.*/#define CONFIG_FILE "fw_env.config"/' tools/env/fw_env*.h
    exit 0
fi

while [ -n "$1" ]; do
    case "$1" in
        --compiled-env=*)
            COMPILED_ENV=${1#--compiled-env=}
            ;;
        --config=*)
            CONFIG=${1#--config=}
            case "$CONFIG" in
                *_config)
                    # Sometimes (Yocto) CONFIG ends in "_config" even though
                    # the actual config file ends in "_defconfig". Correct it.
                    CONFIG="${CONFIG%_config}_defconfig"
                    ;;
            esac
            ;;
        --build-dir=*)
            BUILD_DIR=${1#--build-dir=}
            ;;
        --dep-file=*)
            DEP_FILE=${1#--dep-file=}
            ;;
        --kconfig-fragment=*)
            # Read in all the definitions from that file into variables.
            # Use only line separator as delimiter.
            IFS='
'
            for line in $(cat "${1#--kconfig-fragment=}"); do
                # Replace existing " with \".
                line="${line//\"/\\\"}"
                # Add quotes around value of assignment.
                line="${line/=/=\"}\""
                eval "$line"
            done
            unset IFS
            ;;
        --ubi)
            UBI=1
            ;;
        *)
            echo "Invalid argument: $1"
            exit 1
            ;;
    esac
    shift
done

set -u

patch_all_candidates
