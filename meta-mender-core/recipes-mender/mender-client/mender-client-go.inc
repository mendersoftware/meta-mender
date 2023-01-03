require mender-client.inc

RCONFLICTS:${PN} = "mender-auth"

DESCRIPTION = "Mender tool for doing OTA software updates."
HOMEPAGE = "https://mender.io"

RDEPENDS:${PN}:append:mender-growfs-data:mender-systemd = " parted util-linux-fdisk"
RDEPENDS:${PN}:append:mender-growfs-data:mender-systemd:mender-partlabel = " util-linux-blkid"
RDEPENDS:${PN}:append:mender-growfs-data:mender-systemd:mender-partuuid = " util-linux-blkid"

PACKAGES:append = " mender-modules-gen"

RDEPENDS:mender-modules-gen = "bash"

FILES:mender-modules-gen = " \
    ${bindir}/directory-artifact-gen \
    ${bindir}/single-file-artifact-gen \
    ${bindir}/docker-artifact-gen \
"

FILES:${PN}:append:mender-image:mender-systemd = " \
    ${systemd_unitdir}/system/mender-data-dir.service \
    ${systemd_unitdir}/system/${MENDER_CLIENT}.service.wants/mender-data-dir.service \
"

FILES:${PN}:append:mender-growfs-data:mender-systemd = " \
    ${bindir}/mender-resize-data-part \
    ${systemd_unitdir}/system/mender-grow-data.service \
    ${systemd_unitdir}/system/mender-systemd-growfs-data.service \
    ${systemd_unitdir}/system/data.mount.wants/mender-grow-data.service \
    ${systemd_unitdir}/system/data.mount.wants/mender-systemd-growfs-data.service \
"

FILES:${PN}:append:mender-persist-systemd-machine-id = " \
    ${systemd_unitdir}/system/mender-systemd-machine-id.service \
    ${systemd_unitdir}/system/${MENDER_CLIENT}.service.wants/mender-systemd-machine-id.service \
    ${bindir}/mender-set-systemd-machine-id.sh \
"

FILES:${PN} += "\
    ${datadir}/dbus-1/system.d/io.mender.AuthenticationManager.conf \
    ${datadir}/dbus-1/system.d/io.mender.UpdateManager.conf \
    ${datadir}/mender/identity \
    ${datadir}/mender/identity/mender-device-identity \
    ${datadir}/mender/inventory \
    ${datadir}/mender/inventory/mender-inventory-bootloader-integration \
    ${datadir}/mender/inventory/mender-inventory-hostinfo \
    ${datadir}/mender/inventory/mender-inventory-network \
    ${datadir}/mender/inventory/mender-inventory-os \
    ${datadir}/mender/inventory/mender-inventory-rootfs-type \
    ${datadir}/mender/modules/v3/deb \
    ${datadir}/mender/modules/v3/directory \
    ${datadir}/mender/modules/v3/docker \
    ${datadir}/mender/modules/v3/rpm \
    ${datadir}/mender/modules/v3/script \
    ${datadir}/mender/modules/v3/single-file \
    ${sysconfdir}/udev/mount.blacklist.d/mender \
    /data/mender/device_type \
    /data/mender/mender.conf \
"

FILES:${PN} += "\
    /usr/share/dbus-1/interface \
    /usr/share/dbus-1/interface/io.mender.Update1.xml \
    /usr/share/dbus-1/interface/io.mender.Authentication1.xml \
"


FILES:${PN}-dev += " \
    ${datadir}/dbus-1/interface \
"

MENDER_CLIENT ?= "mender-client"

SYSTEMD_SERVICE:${PN} = "${MENDER_CLIENT}.service"

FILES:${PN} += "\
    ${systemd_unitdir}/system/${MENDER_CLIENT}.service \
"


inherit go
inherit go-ptest

# Go binaries produce unexpected effects that the Yocto QA mechanism doesn't
# like. We disable those checks here.
INSANE_SKIP:${PN} = "ldflags textrel"
INSANE_SKIP:${PN}-ptest = "ldflags textrel"

GO_IMPORT = "github.com/mendersoftware/mender"

GOPTESTBUILDFLAGS:append = " -tags '${_MENDER_TAGS}'"

do_configure:prepend () {
    # Remove all the src present in build if it is not a symbolic link to ${S}
    if [ -d ${B}/src ]; then
        rm -rf ${B}/src
    fi
}

do_configure:append () {
    # Remove the symbolic link created by go.bbclass in do_configure. This is to
    # make sure that the build environment ${B} does not touch ${S} in any way.
    if [ -h ${B}/src ]; then
        rm ${B}/src
    fi
    mkdir -p $(dirname ${B}/src/${GO_IMPORT})
    cp --archive ${S}/src/${GO_IMPORT} ${B}/src/${GO_IMPORT}
}

do_compile() {
    GOPATH="${B}:${S}"
    export GOPATH
    PATH="${B}/bin:$PATH"
    export PATH

    # mender is using vendored dependencies, any 3rd party libraries go to into
    # /vendor directory inside mender source tree. In order for `go build` to pick
    # up vendored deps from our source tree, the mender source tree itself must be
    # located inside $GOPATH/src/${GO_IMPORT}
    #
    # recreate temporary $GOPATH/src/${GO_IMPORT} structure and link our source tree
    mkdir -p ${B}/src/$(dirname ${GO_IMPORT})
    test -e ${B}/src/${GO_IMPORT} || ln -s ${S} ${B}/src/${GO_IMPORT}
    cd ${B}/src/${GO_IMPORT}

    # run verbose build, we should see which dependencies are pulled in
    oe_runmake V=1

    echo "device_type=${MENDER_DEVICE_TYPE}" > ${B}/device_type
}

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
        install-systemd \
        ${@bb.utils.contains('PACKAGECONFIG', 'modules', 'install-modules', '', d)}

    # install inventory scripts
    oe_runmake \
        -C ${B}/src/${GO_IMPORT} \
        V=1 \
        prefix=${D} \
        datadir=${datadir} \
        install-inventory-local-scripts \
        ${@bb.utils.contains('PACKAGECONFIG', 'inventory-network-scripts', 'install-inventory-network-scripts', '', d)}

    # install dbus files
    if ${@bb.utils.contains('PACKAGECONFIG', 'dbus', 'true', 'false', d)}; then
        # install the D-Bus policy file
        oe_runmake \
            -C ${B}/src/${GO_IMPORT} \
            V=1 \
            prefix=${D} \
            datadir=${datadir} \
            install-dbus

        # install the D-Bus interface file(s)
        install -d ${D}${datadir}/dbus-1/interface
        install -m 0644 ${B}/src/${GO_IMPORT}/Documentation/io.mender.*.xml ${D}${datadir}/dbus-1/interface
    fi

    #install our prepared configuration
    install -d ${D}/${sysconfdir}/mender
    install -d ${D}/data/mender
    if [ -f ${B}/transient_mender.conf ]; then
        install -m 0600 ${B}/transient_mender.conf ${D}/${sysconfdir}/mender/mender.conf
    fi
    if [ -f ${B}/persistent_mender.conf ]; then
        install -m 0600 ${B}/persistent_mender.conf ${D}/data/mender/mender.conf
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

    if ${@bb.utils.contains('MENDER_FEATURES', 'mender-image', 'true', 'false', d)}; then
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

# Native overrides, installing scripts for package mender-modules-gen
do_compile:class-native() {
    true
}

do_install:class-native() {
    oe_runmake \
        -C ${B}/src/${GO_IMPORT} \
        V=1 \
        prefix=${D} \
        bindir=${bindir} \
        install-modules-gen
}
