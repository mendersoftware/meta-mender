# Keep this separately from the rest of the .bb file in case that .bb file is
# overridden from another layer.
require u-boot-fw-utils-mender.inc



#-------------------------------------------------------------------------------
# Everything below here is dedicated to providing an automatic OOTB
# u-boot-fw-utils recipe, for those configurations that lack it. It does this by
# reusing the sources from the main U-Boot recipe itself.

LICENSE = "GPL-2.0"
LIC_FILES_CHKSUM = "file://Licenses/README;md5=a2c678cfd4a4d97135585cad908541c6"

PROVIDES = "u-boot-fw-utils"
RPROVIDES_${PN} = "u-boot-fw-utils"

INSANE_SKIP_${PN} = "already-stripped"
EXTRA_OEMAKE_class-target = 'CROSS_COMPILE=${TARGET_PREFIX} CC="${CC} ${CFLAGS} ${LDFLAGS}" HOSTCC="${BUILD_CC} ${BUILD_CFLAGS} ${BUILD_LDFLAGS}" V=1'

S = "${WORKDIR}/git"

def mender_preferred_uboot(d):
    pref_uboot = d.getVar('PREFERRED_PROVIDER_u-boot')
    if pref_uboot in [None, ""]:
        return "u-boot"
    else:
        return pref_uboot
MENDER_PREFERRED_UBOOT = "${@mender_preferred_uboot(d)}"


do_patch() {
    rm -rf ${S}
    mkdir -p ${WORKDIR}
    cd ${WORKDIR}
    tar xzf ${TMPDIR}/mender-u-boot-src.tar.gz
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
    install -m 755 ${S}/tools/env/fw_printenv ${D}${base_sbindir}/fw_printenv
    install -m 755 ${S}/tools/env/fw_printenv ${D}${base_sbindir}/fw_setenv
    install -m 0644 ${S}/tools/env/fw_env.config ${D}${sysconfdir}/fw_env.config
}
