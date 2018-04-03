#!/bin/bash

set -e

BOOTENV_SIZE="${BOOTENV_SIZE:-0x20000}"
BUILDAR="${BUILDAR:-ar}"
BUILDCC="${BUILDCC:-gcc}"
CC=${CC:-${CROSS_COMPILE}gcc}
MAKE="${MAKE:-make}"
MAKEFLAGS="${MAKEFLAGS:-}"

echo $CC


DEBUG=0
SCRIPT_DIR="$(readlink -f "$(dirname "$0")")"

usage() {
    cat <<EOF
$(basename "$0")

Script to produce a patch for U-Boot so it will work with Mender.

--config=<U-Boot machine config>
	The U-Boot config specification that corresponds to your board. This
	usually ends with "_defconfig".
--src-dir=<U-Boot src dir>
	Source directory of U-Boot (will be modified, the diff from the original
	is the resulting patch)
--tmp-dir=<temp dir>"
	Temporary directory to use while working
--debug
	Lots of debug output

Note that all the arguments above can also be passed as environment variables
that are capitalized with dashes changed to underscores.
EOF
}

while [ -n "$1" ]; do
    case "$1" in
        --config=*)
            CONFIG="${1#--config=}"
            ;;
        --src-dir=*)
            SRC_DIR="$(readlink -f "${1#--src-dir=}")"
            ;;
        --tmp-dir=*)
            TMP_DIR="$(readlink -f "${1#--tmp-dir=}")"
            ;;
        --debug)
            DEBUG=1
            MAKEFLAGS="$MAKEFLAGS V=1"
            ;;
        *)
            usage
            exit 1
            ;;
    esac
    shift
done

cat <<EOF
If at any point you get an unexpanded variable, there is probably an argument
you haven't given.
EOF

if [ $DEBUG -eq 1 ]; then
    set -x
    SUB_X=-x
else
    SUB_X=
fi

set -u

rm -rf "$TMP_DIR"
mkdir -p "$(dirname "$TMP_DIR")"
cp -r "$SRC_DIR" "$TMP_DIR"
cd "$TMP_DIR"

# Prepare build.
# Just so that the terminology is clear: BUILDCC refers to the compiler for the
# host that is building the program. CC refers to the compiler for the target
# device. HOSTCC, which is used by U-Boot, is the same as BUILDCC, but this
# doesn't follow gcc's terminology, where "host" is the target device. Hence, we
# stick to gcc's convention, and just reassign BUILDCC to HOSTCC here.
$MAKE HOSTCC="$BUILDCC -DMENDER_AUTO_PROBING" CC="$CC -DMENDER_AUTO_PROBING" "$CONFIG"

# Detect what the build target to the environment tools is. It changed from
# "env" to "envtools" in v2017.09.
grep -q '^tools-all: *env\b' Makefile && ENV_TARGET=env
grep -q '^tools-all: *envtools\b' Makefile && ENV_TARGET=envtools
if [ -z "$ENV_TARGET" ]; then
    echo "Could not determine environment tools target."
    exit 1
fi

# Prepare env tools for host platform.
bash $SUB_X "$SCRIPT_DIR/uboot_auto_patch.sh" --patch-config-file
$MAKE HOSTCC="$BUILDCC -DMENDER_AUTO_PROBING" CC="$BUILDCC -DMENDER_AUTO_PROBING" $ENV_TARGET

# Prepare a fake environment to make work fw_printenv properly. Doesn't have
# to be valid, just existing.
dd if=/dev/zero of=fake-env.txt count=1 bs=$(printf %d "$BOOTENV_SIZE")
cat > fw_env.config <<EOF
fake-env.txt 0 $BOOTENV_SIZE
fake-env.txt 0 $BOOTENV_SIZE
EOF
# Save compiled U-Boot environment
mkdir -p fw_printenv.lock
tools/env/fw_printenv -l fw_printenv.lock > "$TMP_DIR/compiled-environment.txt"
rm -rf fw_printenv.lock

# cmd/.version.o.cmd is automatically built by the build system and contains all
# dependencies for the given source file. We use this to go through all the
# files potentially containing definitions that we need to change. The reason
# for using this instead of simply going through all files, is that we want to
# patch exactly the files that are used in the build, not a lot of unrelated
# files.
$MAKE HOSTCC="$BUILDCC -DMENDER_AUTO_PROBING" CC="$CC -DMENDER_AUTO_PROBING" cmd/version.o

# We now have all the information we need from the build. Start patching!
cd "$SRC_DIR"
bash $SUB_X "$SCRIPT_DIR/uboot_auto_patch.sh" \
     --compiled-env="$TMP_DIR/compiled-environment.txt" \
     --config="$CONFIG" \
     --dep-file="$TMP_DIR"/cmd/.version.o.cmd \
     --env-size="$BOOTENV_SIZE"

set +x

cat <<EOF

********************************************************************************
Finished! Note that if you rerun this script you should clean the source
directory first.
********************************************************************************
EOF
