require mender-client.inc

DESCRIPTION = "Mender tool for doing OTA software updates."
HOMEPAGE = "https://mender.io"

PROVIDES += "mender"
RPROVIDES:${PN} += "mender-auth mender-update"

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
    ${_MENDER_PERSISTENT_DIR}/device_type \
    ${_MENDER_PERSISTENT_DIR}/mender.conf \
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

_MENDER_TAGS = "${@bb.utils.contains('PACKAGECONFIG', 'dbus', '', 'nodbus', d)}"
EXTRA_OEMAKE:append = " TAGS='${_MENDER_TAGS}'"
# Changes to tags are not automatically picked up by the Makefile, so repopulate
# the build directory from scratch if changing this.
do_unpack[vardeps] += "_MENDER_TAGS"

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
