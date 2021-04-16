require mender-client.inc

################################################################################
#-------------------------------------------------------------------------------
# THINGS TO CONSIDER FOR EACH RELEASE:
# - SRC_URI (particularly "branch")
# - SRCREV
# - DEFAULT_PREFERENCE
#-------------------------------------------------------------------------------

SRC_URI = "git://github.com/mendersoftware/mender;protocol=https;branch=2.3.x"

# Tag: 2.3.3
SRCREV = "3bfbbc98db5e841b3484f37855a4442e24cce9cb"

# Enable this in Betas, not in finals.
# Downprioritize this recipe in version selections.
#DEFAULT_PREFERENCE = "-1"

################################################################################

# DO NOT change the checksum here without make sure that ALL licenses (including
# dependencies) are included in the LICENSE variable below. Note that for
# releases, we must check the LIC_FILES_CHKSUM.sha256 file, not the LICENSE
# file.
LIC_FILES_CHKSUM = "file://src/github.com/mendersoftware/mender/LIC_FILES_CHKSUM.sha256;md5=defbf977224ad6ceaf88087f40552a72"
LICENSE = "Apache-2.0 & BSD-2-Clause & BSD-3-Clause & ISC & MIT & OLDAP-2.8"

DEPENDS += "xz"
RDEPENDS_${PN} += "liblzma"

# Not supported in versions < 2.5.0.
_MENDER_PACKAGECONFIG_DEFAULT_remove = "dbus"

do_install() {
    oe_runmake \
        -C ${B}/src/${GO_IMPORT} \
        V=1 \
        prefix=${D} \
        bindir=${bindir} \
        datadir=${datadir} \
        sysconfdir=${sysconfdir} \
        systemd_unitdir=${systemd_unitdir} \
        install-bin \
        install-identity-scripts \
        install-inventory-scripts \
        install-systemd \
        ${@bb.utils.contains('PACKAGECONFIG', 'modules', 'install-modules', '', d)}

    #install our prepared configuration
    install -d ${D}/${sysconfdir}/mender
    install -d ${D}/data/mender
    if [ -f ${B}/transient_mender.conf ]; then
        install -m 0600 ${B}/transient_mender.conf ${D}/${sysconfdir}/mender/mender.conf
    fi
    if [ -f ${B}/persistent_mender.conf ]; then
        install -m 0600 ${B}/persistent_mender.conf ${D}/data/mender/mender.conf
    fi

    #install server certificate
    if [ -f ${WORKDIR}/server.crt ]; then
        install -m 0755 -d $(dirname ${D}${MENDER_CERT_LOCATION})
        install -m 0444 ${WORKDIR}/server.crt ${D}${MENDER_CERT_LOCATION}
        install -m 0755 -d ${D}${localdatadir}/ca-certificates/mender
        install -m 0444 ${WORKDIR}/server.crt ${D}${localdatadir}/ca-certificates/mender/server.crt
    fi

    install -d ${D}/${localstatedir}/lib/mender

    # install artifact verification key, if any.
    if [ -e ${WORKDIR}/artifact-verify-key.pem ]; then
        if [ -n "${MENDER_ARTIFACT_VERIFY_KEY}" ]; then
            bbfatal "You can not specify both MENDER_ARTIFACT_VERIFY_KEY and have artifact-verify-key.pem in SRC_URI."
        fi
        install -m 0444 ${WORKDIR}/artifact-verify-key.pem ${D}${sysconfdir}/mender
    elif [ -n "${MENDER_ARTIFACT_VERIFY_KEY}" ]; then
        install -m 0444 "${MENDER_ARTIFACT_VERIFY_KEY}" ${D}${sysconfdir}/mender/artifact-verify-key.pem
    fi

    if ${@bb.utils.contains('DISTRO_FEATURES', 'mender-image', 'true', 'false', d)}; then
        # symlink /var/lib/mender to /data/mender
        rm -rf ${D}/${localstatedir}/lib/mender
        ln -s /data/mender ${D}/${localstatedir}/lib/mender

        install -m 755 -d ${D}/data/mender
        install -m 444 ${B}/device_type ${D}/data/mender/
    fi

    # Setup blacklist to ensure udev does not automatically mount Mender managed partitions
    install -d ${D}${sysconfdir}/udev/mount.blacklist.d
    echo ${MENDER_ROOTFS_PART_A} > ${D}${sysconfdir}/udev/mount.blacklist.d/mender
    echo ${MENDER_ROOTFS_PART_B} >> ${D}${sysconfdir}/udev/mount.blacklist.d/mender
}
