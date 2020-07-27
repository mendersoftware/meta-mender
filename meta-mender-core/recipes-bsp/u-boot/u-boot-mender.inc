inherit deploy
inherit uboot-config

include u-boot-mender-helpers.inc

DEPENDS += "coreutils-native"

DEPLOYDIR = "${WORKDIR}/deploy-${PN}"

MENDER_UBOOT_AUTO_CONFIGURE ??= "${@bb.utils.contains('DISTRO_FEATURES', 'mender-uboot', '1', '0', d)}"

################################################################################
# Patches.
################################################################################
FILESEXTRAPATHS_prepend := "${THISDIR}/patches:${THISDIR}/files:"

SRC_URI_append_mender-uboot = " file://0001-Add-missing-header-which-fails-on-recent-GCC.patch"
SRC_URI_append_mender-uboot = " file://0002-Generic-boot-code-for-Mender.patch"
SRC_URI_append_mender-uboot = " file://0003-Integration-of-Mender-boot-code-into-U-Boot.patch"

SRC_URI_append_mender-uboot = "${@bb.utils.contains('MENDER_UBOOT_AUTO_CONFIGURE', \
                                                    '1', \
                                                    ' file://0004-Disable-CONFIG_BOOTCOMMAND-and-enable-CONFIG_MENDER_.patch', \
                                                    '', \
                                                    d)}"


################################################################################
# Generic tasks.
################################################################################
do_provide_mender_defines() {
    set -x

    if ! ${@bb.utils.contains('DISTRO_FEATURES', 'mender-uboot', 'true', 'false', d)}; then
        bbfatal "To compile U-Boot with mender you have to add 'mender-uboot' to MENDER_FEATURES_ENABLE or DISTRO_FEATURES."
    fi

    # Since the libubootenv recipe will typically not have access to the proper
    # BOOTENV_SIZE, let's create the fw_env.config file here, so that it can
    # pick it from the deploy directory.
    if [ ! -e "${WORKDIR}/fw_env.config.default" ]; then
        mender_create_fw_env_config_file ${WORKDIR}/fw_env.config.default
    fi

    if [ ${MENDER_UBOOT_CONFIG_SYS_MMC_ENV_PART} -eq "0" ]; then
        # Only check reserved space for bootloader data when the bootloader data is saved to the user partition of the MMC.
        # In cases where it's saved to the boot partition it's not a part of the rootfs size and MENDER_RESERVED_SPACE_BOOTLOADER_DATA
        # can be set to 0. It's up to layer customization to check size and alignment in this case.
        if [ $(expr ${MENDER_RESERVED_SPACE_BOOTLOADER_DATA} % \( ${MENDER_PARTITION_ALIGNMENT} \* 2 \)) -ne 0 ]; then
            bbfatal "MENDER_RESERVED_SPACE_BOOTLOADER_DATA is not an even multiple of MENDER_PARTITION_ALIGNMENT."
        fi

        if [ ${MENDER_BOOTENV_TOTAL_ALIGNED_SIZE} -gt ${MENDER_RESERVED_SPACE_BOOTLOADER_DATA} ]; then
            bbfatal "BOOTENV_SIZE (${BOOTENV_SIZE}) is too big to fit two copies inside MENDER_RESERVED_SPACE_BOOTLOADER_DATA (${MENDER_RESERVED_SPACE_BOOTLOADER_DATA}) with proper alignment. Please either: 1. Increase MENDER_RESERVED_SPACE_BOOTLOADER_DATA manually and make sure it is an *even* multiple of MENDER_PARTITION_ALIGNMENT (${MENDER_PARTITION_ALIGNMENT}). -or- 2. Decrease BOOTENV_SIZE in the U-Boot recipe so that it can fit two copies inside MENDER_RESERVED_SPACE_BOOTLOADER_DATA. Please see https://docs.mender.io/troubleshooting/yocto-project-build for more information."
        fi
    fi

    if [ -n "${MENDER_BOOT_PART}" ]; then
        if ${@bb.utils.contains('DISTRO_FEATURES', 'mender-partuuid', 'true', 'false', d)}; then
            MENDER_BOOT_PART_NUMBER=${MENDER_BOOT_PART}
            MENDER_BOOT_PART_NUMBER_HEX=`mender_number_to_hex ${MENDER_BOOT_PART_NUMBER}`
        else
            MENDER_BOOT_PART_NUMBER=`get_part_number_from_device ${MENDER_BOOT_PART}`
            MENDER_BOOT_PART_NUMBER_HEX=`get_part_number_hex_from_device ${MENDER_BOOT_PART}`
        fi
     fi

    if ${@bb.utils.contains('DISTRO_FEATURES', 'mender-partuuid', 'true', 'false', d)}; then
        MENDER_ROOTFS_PART_A_NUMBER=${MENDER_ROOTFS_PART_A}
        MENDER_ROOTFS_PART_A_NUMBER_HEX=`mender_number_to_hex ${MENDER_ROOTFS_PART_A_NUMBER}`
        MENDER_ROOTFS_PART_B_NUMBER=${MENDER_ROOTFS_PART_B}
        MENDER_ROOTFS_PART_B_NUMBER_HEX=`mender_number_to_hex ${MENDER_ROOTFS_PART_B_NUMBER}`
    else
        MENDER_ROOTFS_PART_A_NUMBER=`get_part_number_from_device ${MENDER_ROOTFS_PART_A}`
        MENDER_ROOTFS_PART_A_NUMBER_HEX=`get_part_number_hex_from_device ${MENDER_ROOTFS_PART_A}`
        MENDER_ROOTFS_PART_B_NUMBER=`get_part_number_from_device ${MENDER_ROOTFS_PART_B}`
        MENDER_ROOTFS_PART_B_NUMBER_HEX=`get_part_number_hex_from_device ${MENDER_ROOTFS_PART_B}`
    fi

    if [ -n "${MENDER_UBOOT_STORAGE_INTERFACE}" ]; then
        MENDER_UBOOT_STORAGE_INTERFACE=${MENDER_UBOOT_STORAGE_INTERFACE}
    else
        MENDER_UBOOT_STORAGE_INTERFACE=`get_uboot_interface_from_device ${MENDER_STORAGE_DEVICE}`
    fi
    if [ -n "${MENDER_UBOOT_STORAGE_DEVICE}" ]; then
        MENDER_UBOOT_STORAGE_DEVICE=${MENDER_UBOOT_STORAGE_DEVICE}
    else
        MENDER_UBOOT_STORAGE_DEVICE=`get_uboot_device_from_device ${MENDER_STORAGE_DEVICE}`
    fi

    if [ -n "${MENDER_KERNEL_IMAGETYPE_FORCE}" ]; then
        MENDER_KERNEL_IMAGETYPE="${MENDER_KERNEL_IMAGETYPE_FORCE}"
    elif [ -n "${KERNEL_IMAGETYPE}" ]; then
        MENDER_KERNEL_IMAGETYPE="${KERNEL_IMAGETYPE}"
    else
        MENDER_KERNEL_IMAGETYPE="zImage"
    fi

    case "$MENDER_KERNEL_IMAGETYPE" in
        *uImage*|*fitImage*)
            MENDER_BOOT_KERNEL_TYPE=bootm
            ;;
        *zImage*)
            MENDER_BOOT_KERNEL_TYPE=bootz
            ;;
        Image*)
            MENDER_BOOT_KERNEL_TYPE=booti
            ;;
        *)
            MENDER_BOOT_KERNEL_TYPE=bootz
            ;;
    esac

    MENDER_DTB_NAME=$(mender_get_clean_kernel_devicetree)

    HEX_MENDER_UBOOT_ENV_STORAGE_DEVICE_OFFSET_1="$(printf 0x%x "${MENDER_UBOOT_ENV_STORAGE_DEVICE_OFFSET_1}")"
    HEX_MENDER_UBOOT_ENV_STORAGE_DEVICE_OFFSET_2="$(printf 0x%x "${MENDER_UBOOT_ENV_STORAGE_DEVICE_OFFSET_2}")"

    if [ -n "${MENDER_UBOOT_PRE_SETUP_COMMANDS}" ]; then
        MENDER_UBOOT_PRE_SETUP_COMMANDS="${MENDER_UBOOT_PRE_SETUP_COMMANDS}"
    fi

    if [ -n "${MENDER_UBOOT_POST_SETUP_COMMANDS}" ]; then
        MENDER_UBOOT_POST_SETUP_COMMANDS="${MENDER_UBOOT_POST_SETUP_COMMANDS}"
    fi

    cat > ${S}/include/config_mender_defines.h <<EOF
/* AUTOGENERATED FILE - DO NOT EDIT! */
/* This file is provided by the meta-mender layer. */

#ifndef HEADER_CONFIG_MENDER_DEFINES_H
#define HEADER_CONFIG_MENDER_DEFINES_H

/* Shell variables */
#define MENDER_BOOT_PART_NUMBER $MENDER_BOOT_PART_NUMBER
#define MENDER_BOOT_PART_NUMBER_HEX $MENDER_BOOT_PART_NUMBER_HEX
#define MENDER_ROOTFS_PART_A_NUMBER $MENDER_ROOTFS_PART_A_NUMBER
#define MENDER_ROOTFS_PART_A_NUMBER_HEX $MENDER_ROOTFS_PART_A_NUMBER_HEX
#define MENDER_ROOTFS_PART_B_NUMBER $MENDER_ROOTFS_PART_B_NUMBER
#define MENDER_ROOTFS_PART_B_NUMBER_HEX $MENDER_ROOTFS_PART_B_NUMBER_HEX
#define MENDER_UBOOT_STORAGE_INTERFACE "$MENDER_UBOOT_STORAGE_INTERFACE"
#define MENDER_UBOOT_STORAGE_DEVICE $MENDER_UBOOT_STORAGE_DEVICE
#define MENDER_UBOOT_CONFIG_SYS_MMC_ENV_PART ${MENDER_UBOOT_CONFIG_SYS_MMC_ENV_PART}

/* BB variables. */
#define MENDER_STORAGE_DEVICE "${MENDER_STORAGE_DEVICE}"
#define MENDER_STORAGE_DEVICE_BASE "${MENDER_STORAGE_DEVICE_BASE}"
#define MENDER_UBOOT_ENV_STORAGE_DEVICE_OFFSET_1 $HEX_MENDER_UBOOT_ENV_STORAGE_DEVICE_OFFSET_1
#define MENDER_UBOOT_ENV_STORAGE_DEVICE_OFFSET_2 $HEX_MENDER_UBOOT_ENV_STORAGE_DEVICE_OFFSET_2
#define MENDER_ROOTFS_PART_A_NAME "${MENDER_ROOTFS_PART_A_NAME}"
#define MENDER_ROOTFS_PART_B_NAME "${MENDER_ROOTFS_PART_B_NAME}"

/* For sanity checks. */
#define MENDER_BOOTENV_SIZE ${BOOTENV_SIZE}

#define MENDER_BOOT_KERNEL_TYPE "$MENDER_BOOT_KERNEL_TYPE"
#define MENDER_KERNEL_NAME "$MENDER_KERNEL_IMAGETYPE"
#define MENDER_DTB_NAME "$MENDER_DTB_NAME"
#define MENDER_UBOOT_PRE_SETUP_COMMANDS "$MENDER_UBOOT_PRE_SETUP_COMMANDS"
#define MENDER_UBOOT_POST_SETUP_COMMANDS "$MENDER_UBOOT_POST_SETUP_COMMANDS"
EOF

    if ${@bb.utils.contains('DISTRO_FEATURES', 'mender-ubi', "true", "false", d)}; then
        if [ -z "${MENDER_MTDIDS}" ]; then
            bbfatal "MENDER_MTDIDS is empty. Please set it to valid value for your board. An example is 'nor0=40000000.flash'."
        fi

        if ! grep -q UBI_IOCVOLUP ${S}/tools/env/fw_env.c; then
            bbwarn "Detected U-Boot without support for direct read/write to UBI volumes. Mender normally expects this unless you have a custom setup. Consider backporting the patch at http://git.denx.de/?p=u-boot.git;a=commitdiff;h=34255b92e6e68941ab1134299faa86acc5a1abc8 to your U-Boot sources."
        fi

        cat >> ${S}/include/config_mender_defines.h <<EOF
#define MENDER_MTD_REQUIRED
#define MENDER_UBI
#define MENDER_MTD_UBI_DEVICE_NAME "${MENDER_MTD_UBI_DEVICE_NAME}"
#define MENDER_MTDIDS "${MENDER_MTDIDS}"
#define MENDER_MTDPARTS "${MENDER_MTDPARTS}"
EOF
    fi

    cat >> ${S}/include/config_mender_defines.h <<EOF
#endif /* !HEADER_CONFIG_MENDER_DEFINES_H */
EOF

    # Provide a Kconfig fragment containing various defines we need. If auto
    # configure is off, this will only be used for checking. If it is on, then
    # the auto-patcher will use it to patch, and can do so without having to
    # pass a lot of arguments or environment variables.
    cat > ${S}/mender_Kconfig_fragment <<EOF
CONFIG_ENV_SIZE=${BOOTENV_SIZE}
EOF

    if ${@bb.utils.contains('DISTRO_FEATURES', 'mender-ubi', "true", "false", d)}; then
        cat >> ${S}/mender_Kconfig_fragment <<EOF
CONFIG_MTDIDS_DEFAULT="${MENDER_MTDIDS}"
CONFIG_MTDPARTS_DEFAULT="mtdparts=${MENDER_MTDPARTS}"
CONFIG_ENV_UBI_PART="${MENDER_MTD_UBI_DEVICE_NAME}"
CONFIG_ENV_UBI_VOLUME="u-boot-env-1"
CONFIG_ENV_UBI_VOLUME_REDUND="u-boot-env-2"
CONFIG_ENV_OFFSET=0x0
CONFIG_ENV_OFFSET_REDUND=0x0
EOF
    else
        cat >> ${S}/mender_Kconfig_fragment <<EOF
CONFIG_ENV_OFFSET=$HEX_MENDER_UBOOT_ENV_STORAGE_DEVICE_OFFSET_1
CONFIG_ENV_OFFSET_REDUND=$HEX_MENDER_UBOOT_ENV_STORAGE_DEVICE_OFFSET_2
CONFIG_SYS_MMC_ENV_PART=${MENDER_UBOOT_CONFIG_SYS_MMC_ENV_PART}
CONFIG_SYS_MMC_ENV_DEV=$MENDER_UBOOT_STORAGE_DEVICE
EOF
    fi
}
python() {
    if bb.utils.contains('DISTRO_FEATURES', 'mender-uboot', True, False, d):
        bb.build.addtask('do_provide_mender_defines', 'do_configure', 'do_patch', d)
}

do_configure_prepend_mender-uboot() {
    # Do a sanity check on some defines. The reason this is necessary, even
    # though they are defined by us, is that there are two ways the defines can
    # make it into the code, Kconfig and source code, and several things can
    # happen:
    #
    # 1) The option doesn't use Kconfig: In this case we defer to the patch
    #    file, where we either define each variable, or, if already defined,
    #    check that their values are correct. Unfortunately we cannot check
    #    strings because this is impossible with the C preprocessor, so in that
    #    case we just have to trust that the define is correct.
    #
    # 2) The option uses Kconfig, but something is preventing the option from
    #    reaching the .config file. This sometimes happens when an option is
    #    conditionally dependent on some other option. If this happens we should
    #    produce an error. Unfortunately there is no good way to separate this
    #    case from case number 1, because both cases will just exhibit not being
    #    in .config. So we will use the same remedy as for case number 1, and
    #    hope that defining it in the header will work.
    #
    # 3) The option uses Kconfig, and is in .config. In this case we just check
    #    that its value is correct.

    # Calling this here is slightly evil, but we need its results, and we cannot
    # wait until after the do_configure stage is done. The reason is a bug in
    # poky. At the time of writing, the cml1_do_configure() is called from the
    # uboot build, and contains the following: `yes '' | oe_runmake
    # oldconfig`. The problem with this statement is that if the configuration
    # fails to converge, which can happen if a configuration option doesn't have
    # a default (CONFIG_ENV_OFFSET), then this will loop forever, filling up the
    # log, and all the memory of the build host. Therefore this check, which
    # detects such options being missing, needs to run before do_configure.
    if [ ! -e ${B}/.config ]; then
        oe_runmake -C ${S} O=${B} ${UBOOT_MACHINE}
    fi

    # Split only on newlines.
    IFS='
'
    for line in $(cat "${S}/mender_Kconfig_fragment"); do
        key="$(echo "$line" | sed -e 's/=.*//')"
        if egrep "^($key=|# $key is not set\$)" ${B}/.config; then
            # We found the option. Check that it's correct.
            if ! fgrep "$line" ${B}/.config; then
                wrong_entry="$(fgrep "$key" ${B}/.config)"
                msg="$(printf "U-Boot configuration %s has setting:\n%s\nbut Mender expects:\n%s\nPlease fix U-Boot's configuration file." \
                    "${UBOOT_MACHINE}" \
                    "$wrong_entry" \
                    "$line")"
                bbfatal "$msg"
            fi
        fi
    done
    unset IFS
}

do_compile_append_mender-uboot_mender-ubi() {
    # Doing this in do_compile instead of do_configure is actually a bit late,
    # but the U-Boot recipe doesn't separate between the stages.

    config_value="$(fgrep 'CONFIG_MTDIDS_DEFAULT=' ${B}/.config || true)"
    if [ -n "$config_value" ] && ! fgrep 'CONFIG_MTDIDS_DEFAULT="${MENDER_MTDIDS}"' ${B}/.config; then
        bbwarn "CONFIG_MTDIDS_DEFAULT ('$config_value') in U-Boot's .config file is not the same as MENDER_MTDIDS ('MENDER_MTDIDS=\"${MENDER_MTDIDS}\"')"
    fi

    config_value="$(fgrep 'CONFIG_MTDPARTS_DEFAULT=' ${B}/.config || true)"
    if [ -n "$config_value" ] && ! fgrep 'CONFIG_MTDPARTS_DEFAULT="mtdparts=${MENDER_MTDPARTS}"' ${B}/.config; then
        bbwarn "CONFIG_MTDPARTS_DEFAULT ('$config_value') in U-Boot's .config file is not the same as MENDER_MTDPARTS ('MENDER_MTDPARTS=\"mtdparts=${MENDER_MTDPARTS}\"')"
    fi
}

SRC_URI_append_mender-uboot = "${@bb.utils.contains('MENDER_UBOOT_AUTO_CONFIGURE', \
                                                    '1', \
                                                    ' file://uboot_auto_configure.sh \
                                                      file://uboot_auto_patch.sh \
                                                      file://add_kconfig_option_with_depends.py \
                                                      file://boolean.py', \
                                                    '', \
                                                    d)}"

MENDER_UBOOT_TMP_SRC = "${WORKDIR}/tmp-src"
MENDER_UBOOT_OLD_SRC = "${WORKDIR}/old-src"

do_mender_uboot_auto_configure() {
    if [ -n "${EXTERNALSRC}" ]; then
        bbwarn "Skipping U-Boot auto-configuration when EXTERNALSRC is set. Would change the source files. If you need the patch, turn off EXTERNALSRC, call 'bitbake -c save_mender_auto_configured_patch u-boot' to generate a patch, and then apply that to your work tree and reenable EXTERNALSRC."
        exit 0
    fi

    # Try to detect whether Mender specific porting patches have already been
    # applied. To do this, we can look for "mender_setup" anywhere outside of
    # env_mender.h, since the old instructions would put it outside, and in the
    # new auto-patching it is always inside.
    if [ `fgrep -rl mender_setup ${S} | fgrep -v /env_mender.h | wc -l` -gt 0 ]; then
        bbwarn 'Detected previously applied Mender patch on top of U-Boot. Probably U-Boot will either produce compile errors or misbehave. It is advised to either remove any Mender specific patches, or disable the auto-patching by setting MENDER_UBOOT_AUTO_CONFIGURE = "0" somewhere in the U-Boot recipe.'
    fi

    cd ${WORKDIR}

    # This is for diffing and displaying the patch later, if necessary.
    rm -rf ${MENDER_UBOOT_OLD_SRC}
    cp -r "${S}" ${MENDER_UBOOT_OLD_SRC}

    # Strip leading and trailing whitespace, then newline divide.
    MENDER_UBOOT_MACHINE="$(echo "${UBOOT_MACHINE}" | sed -r 's/(^\s*)|(\s*$)//g; s/\s+/\n/g')"

    if [ -z "$MENDER_UBOOT_MACHINE" ]; then
        bbfatal "Did not find a machine specified in UBOOT_MACHINE"
        exit 1
    fi

    MACHINE_COUNT=$(echo "$MENDER_UBOOT_MACHINE" | wc -l)
    if [ "$MACHINE_COUNT" -ne 1 ]; then
        bbwarn "Found more than one machine specified in UBOOT_MACHINE. Only one should be specified. Choosing the last one."
        MENDER_UBOOT_MACHINE="$(echo "$MENDER_UBOOT_MACHINE" | tail -1)"
    fi

    env \
        BUILDCC="${BUILD_CC}" \
        CROSS_COMPILE="${TARGET_PREFIX}" \
        ./uboot_auto_configure.sh \
        --config=$MENDER_UBOOT_MACHINE \
        --src-dir=${S} \
        --tmp-dir=${MENDER_UBOOT_TMP_SRC} \
        --kconfig-fragment=${S}/mender_Kconfig_fragment \
        ${@bb.utils.contains('DISTRO_FEATURES', 'mender-ubi', '--ubi', '', d)} \
        --debug
}
do_mender_uboot_auto_configure[depends] = "${PN}:do_prepare_recipe_sysroot"
# This is for the externalsrc class: Make sure we don't try to edit a user
# provided directory. Only temporary checkouts from source control should be
# edited.
SRCTREECOVEREDTASKS_append = " do_mender_uboot_auto_configure"

do_save_mender_auto_configured_patch() {
    diff -r -u ${MENDER_UBOOT_OLD_SRC} ${S} > ${WORKDIR}/mender_auto_configured.patch || true

    # Get rid of absolute paths in the patch.
    sed -rie '/---|\+\+\+/ { s%${MENDER_UBOOT_OLD_SRC}%a%; s%${S}%b% }' ${WORKDIR}/mender_auto_configured.patch

    # "bbnote" might be more appropriate here, but it doesn't always display.
    bbwarn "Auto configured U-Boot patch has been stored in ${WORKDIR}/mender_auto_configured.patch"
}

python() {
    if not bb.utils.contains('DISTRO_FEATURES', 'mender-uboot', True, False, d):
        return

    if bb.utils.contains('MENDER_UBOOT_AUTO_CONFIGURE', '1', True, False, d):
        bb.build.addtask('do_mender_uboot_auto_configure', 'do_configure', 'do_provide_mender_defines', d)
        bb.build.addtask('do_save_mender_auto_configured_patch', '', 'do_mender_uboot_auto_configure', d)
}

# Just to have a task if mender-uboot is not defined.
do_deploy_append() {
    :
}
do_deploy_append_mender-uboot() {
    # Copy script to the deploy area with u-boot, uImage, and rootfs
    if [ -e ${WORKDIR}/uEnv.txt ] ; then
        install -d ${DEPLOYDIR}
        install -m 0444 ${WORKDIR}/uEnv.txt ${DEPLOYDIR}
    fi

    # Creates the blob that will be the U-Boot environment, with proper
    # alignment. This will be used later by the image creation recipe. The file
    # is filled with null right now, although it could be filled with the actual
    # environment. For now we're primarily interested in the size.
    # Note: We cannot use a sparse file here, even though it's filled with
    # zeros, because the build process uses "du" to determine the size of this
    # file.
    dd if=/dev/zero of=${WORKDIR}/uboot.env bs=${MENDER_BOOTENV_TOTAL_ALIGNED_SIZE} count=1
    install -m 644 ${WORKDIR}/uboot.env ${DEPLOYDIR}/uboot.env

    install -m 644 ${WORKDIR}/fw_env.config.default ${DEPLOYDIR}/fw_env.config.default
}
addtask deploy after do_compile before do_package

# Ignore this, only used for testing.
# The reason it's here is so that the test URI is appended last.
TEST_SRC_URI_APPEND ??= ""
python() {
    if d.getVar('TEST_SRC_URI_APPEND'):
        d.setVar('SRC_URI', "%s %s" % (d.getVar('SRC_URI'), d.getVar('TEST_SRC_URI_APPEND')))
}
