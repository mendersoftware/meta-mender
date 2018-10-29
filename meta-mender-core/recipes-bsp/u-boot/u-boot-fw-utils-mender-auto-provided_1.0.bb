# Keep this separately from the rest of the .bb file in case that .bb file is
# overridden from another layer.
require u-boot-fw-utils-mender.inc



#-------------------------------------------------------------------------------
# Everything below here is dedicated to providing an automatic OOTB
# u-boot-fw-utils recipe, for those configurations that lack it. It does this by
# reusing the sources from the main U-Boot recipe itself.


LICENSE = "GPL-2.0"
# Specifying a dummy file here is slightly evil, but the problem is that since
# this is a special recipe which uses source code coming from any odd U-Boot
# version imaginable, it is not possible to use a stable checksum pointing to a
# file from within that source. It is pretty unlikely that U-Boot will change
# license, so use this for now.
LIC_FILES_CHKSUM = "file://dummy-license.txt;md5=f02e326f800ee26f04df7961adbf7c0a"

PROVIDES = "u-boot-fw-utils"
RPROVIDES_${PN} = "u-boot-fw-utils"

INSANE_SKIP_${PN} = "already-stripped"
EXTRA_OEMAKE_class-target = 'CROSS_COMPILE=${TARGET_PREFIX} CC="${CC} ${CFLAGS} ${LDFLAGS}" HOSTCC="${BUILD_CC} ${BUILD_CFLAGS} ${BUILD_LDFLAGS}" V=1'
DEPENDS += "bison-native"

S = "${WORKDIR}/src-tar"

def mender_preferred_uboot(d):
    pref_uboot = d.getVar('PREFERRED_PROVIDER_u-boot')
    if pref_uboot in [None, ""]:
        pref_bootloader = d.getVar('PREFERRED_PROVIDER_virtual/bootloader')
        if pref_bootloader and pref_bootloader.startswith("u-boot"):
            return pref_bootloader
        else:
            return "u-boot"
    else:
        return pref_uboot
MENDER_PREFERRED_UBOOT = "${@mender_preferred_uboot(d)}"


do_patch() {
    rm -rf ${S}
    mkdir -p ${WORKDIR}
    cd ${WORKDIR}
    tar xzf ${TMPDIR}/mender-u-boot-src.tar.gz

    # See LIC_FILES_CHKSUM.
    echo dummy > ${S}/dummy-license.txt
}
do_patch[depends] += "${MENDER_PREFERRED_UBOOT}:do_mender_tar_src"

do_compile () {
    oe_runmake ${UBOOT_MACHINE}

    # Detect what the build target to the environment tools is. It changed from
    # "env" to "envtools" in v2017.09.
    grep -q '^tools-all: *env\b' Makefile && ENV_TARGET=env
    grep -q '^tools-all: *envtools\b' Makefile && ENV_TARGET=envtools
    if [ -z "$ENV_TARGET" ]; then
        echo "Could not determine environment tools target."
        exit 1
    fi

    oe_runmake $ENV_TARGET
}

do_install () {
    install -d ${D}${base_sbindir}
    install -d ${D}${sysconfdir}
    install -m 755 ${B}/tools/env/fw_printenv ${D}${base_sbindir}/fw_printenv
    install -m 755 ${B}/tools/env/fw_printenv ${D}${base_sbindir}/fw_setenv
    install -m 0644 ${B}/tools/env/fw_env.config ${D}${sysconfdir}/fw_env.config
}
