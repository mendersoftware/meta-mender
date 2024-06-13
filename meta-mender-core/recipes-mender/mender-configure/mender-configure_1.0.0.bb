require mender-configure.inc

################################################################################
#-------------------------------------------------------------------------------
# THINGS TO CONSIDER FOR EACH RELEASE:
# - SRC_URI (particularly "branch")
# - SRCREV
# - DEFAULT_PREFERENCE
#-------------------------------------------------------------------------------

SRC_URI = "git://github.com/mendersoftware/mender-configure-module;protocol=https;branch=1.0.x"

# Tag: 1.0.0
SRCREV = "bfa3275ced268b5aedfe74c8c537c4e32a9b2851"

# Enable this in Betas, and in branches that cannot carry this major version as
# default.
# Downprioritize this recipe in version selections.
#DEFAULT_PREFERENCE = "-1"

################################################################################

# DO NOT change the checksum here without make sure that ALL licenses (including
# dependencies) are included in the LICENSE variable below.
LIC_FILES_CHKSUM = " \
    file://LICENSE;md5=fbe9cd162201401ffbb442445efecfdc \
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
