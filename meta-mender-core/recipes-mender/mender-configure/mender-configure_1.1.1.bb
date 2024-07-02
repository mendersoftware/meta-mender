require mender-configure.inc

################################################################################
#-------------------------------------------------------------------------------
# THINGS TO CONSIDER FOR EACH RELEASE:
# - SRC_URI (particularly "branch")
# - SRCREV
# - DEFAULT_PREFERENCE
#-------------------------------------------------------------------------------

SRC_URI = "git://github.com/mendersoftware/mender-configure-module;protocol=https;branch=1.1.x"

# Tag: 1.1.1
SRCREV = "d071e350b98f90023c1b1edfed4cb17aba681ef0"

# Enable this in Betas, and in branches that cannot carry this major version as
# default.
# Downprioritize this recipe in version selections.
#DEFAULT_PREFERENCE = "-1"

################################################################################

# DO NOT change the checksum here without make sure that ALL licenses (including
# dependencies) are included in the LICENSE variable below.
LIC_FILES_CHKSUM = " \
    file://LICENSE;md5=b4b4cfdaea6d61aa5793b92efd42e081 \
"
LICENSE = "Apache-2.0"

# mender-configure 1.1.1 and earlier are not usrmerge ready and the service file install path
# is hardcoded to /lib/systemd/system/
do_install:append:mender-systemd() {
    if ${@bb.utils.contains('DISTRO_FEATURES', 'usrmerge', 'true', 'false', d)}; then
        mkdir -p ${D}/${systemd_system_unitdir}
        mv ${D}/lib/systemd/system/mender-configure-apply-device-config.service \
            ${D}/${systemd_system_unitdir}/mender-configure-apply-device-config.service
        rmdir ${D}/lib/systemd/system ${D}/lib/systemd ${D}/lib
    fi
}
