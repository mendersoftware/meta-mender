inherit mender-licensing

BBCLASSEXTEND = "native"
RDEPENDS:${PN}:class-native = ""
DEPENDS:class-native = ""

DESCRIPTION = "Mender tool for doing OTA software updates."
HOMEPAGE = "https://mender.io"

MENDER_SERVER_URL ?= "https://docker.mender.io"
# Tenant token
MENDER_TENANT_TOKEN ?= "dummy"
SYSTEMD_AUTO_ENABLE ?= "enable"
MENDER_UPDATE_POLL_INTERVAL_SECONDS ?= "1800"
MENDER_INVENTORY_POLL_INTERVAL_SECONDS ?= "28800"
MENDER_RETRY_POLL_INTERVAL_SECONDS ?= "300"

PROVIDES += "mender"
RPROVIDES:${PN} += "mender-auth mender-update"

RDEPENDS:${PN}:append:mender-growfs-data:mender-systemd = " parted util-linux-fdisk"
RDEPENDS:${PN}:append:mender-growfs-data:mender-systemd:mender-partlabel = " util-linux-blkid"
RDEPENDS:${PN}:append:mender-growfs-data:mender-systemd:mender-partuuid = " util-linux-blkid"

RRECOMMENDS:${PN}:append = " ca-certificates"

RDEPENDS:mender-modules-gen = "bash"

PACKAGES:append = " mender-modules-gen"

_MENDER_PACKAGECONFIG_DEFAULT = "dbus modules inventory-network-scripts"
PACKAGECONFIG ?= "${_MENDER_PACKAGECONFIG_DEFAULT}"

PACKAGECONFIG:append:class-target = "${@bb.utils.contains('MENDER_FEATURES', 'mender-uboot', ' u-boot', '', d)}"
PACKAGECONFIG:append:class-target = "${@bb.utils.contains('MENDER_FEATURES', 'mender-grub', ' grub', '', d)}"

PACKAGECONFIG[u-boot] = ",,,libubootenv-bin"
PACKAGECONFIG[grub] = ",,,grub-editenv grub-mender-grubenv"

# The docker module depends on bash, and of course on docker. However, docker is
# a very large requirement, which we will not mandate. Bash however, we require,
# because otherwise the Yocto QA checks will complain.
PACKAGECONFIG[modules] = ",,,bash"
PACKAGECONFIG[inventory-network-scripts] = ",,,"

PACKAGECONFIG[dbus] = ",,glib-2.0,glib-2.0"

# NOTE: Splits the mender.conf file by default into a transient and a persistent config. Needs to be
# explicitly disabled if this is not to apply.
PACKAGECONFIG[split-mender-config] = ",,,"
PACKAGECONFIG:append = " split-mender-config"

S = "${WORKDIR}/git"
B = "${WORKDIR}/build"

inherit pkgconfig
inherit systemd

SYSROOT_DIRS += "/data"

SRC_URI:append:mender-image:mender-systemd = " \
    file://mender-data-dir.service \
"

SRC_URI:append:mender-persist-systemd-machine-id = " \
    file://mender-systemd-machine-id.service \
    file://mender-set-systemd-machine-id.sh \
"

SRC_URI:append:mender-growfs-data:mender-systemd = " \
    file://mender-resize-data-part.sh.in \
    file://mender-grow-data.service \
    file://mender-systemd-growfs-data.service \
"

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


FILES:${PN}-dev:append = " \
    ${datadir}/dbus-1/interfaces \
    ${datadir}/dbus-1/interfaces/io.mender.Update1.xml \
    ${datadir}/dbus-1/interfaces/io.mender.Authentication1.xml \
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

_MENDER_PERSISTENT_DIR = "${localstatedir}/lib/mender"
_MENDER_PERSISTENT_DIR:mender-image = "/data/mender"

python do_prepare_mender_conf() {
    import json

    # If a mender.conf has been provided in SRC_URI, merge this with the
    # settings we generate. The settings specified by variables take precedence.
    src_conf = os.path.join(d.getVar("WORKDIR"), "mender.conf")
    if os.path.exists(src_conf):
        bb.debug(1, "mender.conf already present in ${WORKDIR}, merging with generated settings.")
        fd = open(src_conf)
        transient_conf = json.load(fd)
        fd.close()
    else:
        bb.debug(1, "mender.conf not present in ${WORKDIR}, generating a new one.")
        transient_conf = {}
    def conf_maybe_add(key, value, getvar, integer):
        if getvar:
            warn_str = "variable '%s'" % value
            value = d.getVar(value)
        else:
            warn_str = "automatically provided settings"
        if value is not None and value != "":
            if transient_conf.get(key) is not None and transient_conf[key] != value:
                bb.warn("Configuration key '%s', found in mender.conf, conflicts with %s. Choosing the latter." % (key, warn_str))
            if integer:
                transient_conf[key] = int(value)
            else:
                transient_conf[key] = value

    key_in_src_uri = os.path.exists(os.path.join(d.getVar("WORKDIR"), "artifact-verify-key.pem"))
    key_in_var = d.getVar("MENDER_ARTIFACT_VERIFY_KEY") not in [None, ""]

    # Add new variable -> config assignments here.
    if key_in_src_uri or key_in_var:
        conf_maybe_add("ArtifactVerifyKey", "%s/mender/artifact-verify-key.pem" % d.getVar("sysconfdir"), getvar=False, integer=False)
    conf_maybe_add("InventoryPollIntervalSeconds", "MENDER_INVENTORY_POLL_INTERVAL_SECONDS", getvar=True, integer=True)
    # Mandatory variables - will always exist
    conf_maybe_add("RetryPollIntervalSeconds", "MENDER_RETRY_POLL_INTERVAL_SECONDS", getvar=True, integer=True)
    conf_maybe_add("RootfsPartA", "MENDER_ROOTFS_PART_A", getvar=True, integer=False)
    conf_maybe_add("RootfsPartB", "MENDER_ROOTFS_PART_B", getvar=True, integer=False)
    conf_maybe_add("ServerURL", "MENDER_SERVER_URL", getvar=True, integer=False)
    conf_maybe_add("UpdatePollIntervalSeconds", "MENDER_UPDATE_POLL_INTERVAL_SECONDS", getvar=True, integer=True)

    # Tenant-token is optional, but falls back to a default-value set in source code
    conf_maybe_add("TenantToken", "MENDER_TENANT_TOKEN", getvar=True, integer=False)

    # Add the update control configurations if set
    conf_maybe_add("UpdateControlMapExpirationTimeSeconds", "MENDER_UPDATE_CONTROL_MAP_EXPIRATION_TIME_SECONDS", getvar=True, integer=True)
    conf_maybe_add("UpdateControlMapBootExpirationTimeSeconds", "MENDER_UPDATE_CONTROL_MAP_BOOT_EXPIRATION_TIME_SECONDS", getvar=True, integer=True)

    # Filter returns the variables that are present in both instances.
    # Thus no misspelled variables will ever enter the persistent configuration during migration.
    persistent_configs = bb.utils.filter("MENDER_PERSISTENT_CONFIGURATION_VARS", d.getVar("MENDER_CONFIGURATION_VARS"), d)

    persistent_conf = {}

    # Extract the variables that are destined for the persistent mender-configuration.
    if bb.utils.contains('PACKAGECONFIG', 'split-mender-config', True, False, d):
        for config_var in transient_conf:
            if config_var in persistent_configs:
                persistent_conf[config_var] = transient_conf[config_var]

        # Remove the configurations from the transient conf that are already in the persistent configuration.
        for config_var in persistent_conf:
            del transient_conf[config_var]

        dst_conf = os.path.join(d.getVar("B"), "persistent_mender.conf")
        fd = open(dst_conf, "w")
        json.dump(persistent_conf, fd, indent=4, sort_keys=True)
        fd.close()

    dst_conf = os.path.join(d.getVar("B"), "transient_mender.conf")
    fd = open(dst_conf, "w")
    json.dump(transient_conf, fd, indent=4, sort_keys=True)
    fd.close()

}
addtask do_prepare_mender_conf after do_compile before do_install
do_prepare_mender_conf[vardeps] = " \
    MENDER_ARTIFACT_VERIFY_KEY \
    MENDER_INVENTORY_POLL_INTERVAL_SECONDS \
    MENDER_RETRY_POLL_INTERVAL_SECONDS \
    MENDER_ROOTFS_PART_A \
    MENDER_ROOTFS_PART_B \
    MENDER_SERVER_URL \
    MENDER_TENANT_TOKEN \
    MENDER_UPDATE_POLL_INTERVAL_SECONDS \
    MENDER_PERSISTENT_CONFIGURATION_VARS \
"

do_compile:append() {
    echo "device_type=${MENDER_DEVICE_TYPE}" > ${B}/device_type
}

do_install:append() {
    if ${@bb.utils.contains('MENDER_FEATURES', 'mender-image', 'true', 'false', d)}; then
        # symlink /var/lib/mender to /data/mender
        install -m 755 -d ${D}/${localstatedir}/lib
        ln -s /data/mender ${D}/${localstatedir}/lib/mender

        install -m 755 -d ${D}/data/mender
    else
        install -d ${D}/${localstatedir}/lib/mender
    fi

    install -m 444 ${B}/device_type ${D}${_MENDER_PERSISTENT_DIR}/

    #install our prepared configuration
    install -d ${D}/${sysconfdir}/mender
    if [ -f ${B}/transient_mender.conf ]; then
        install -m 0600 ${B}/transient_mender.conf ${D}/${sysconfdir}/mender/mender.conf
    fi
    if [ -f ${B}/persistent_mender.conf ]; then
        install -m 0600 ${B}/persistent_mender.conf ${D}${_MENDER_PERSISTENT_DIR}/mender.conf
    fi

    # install artifact verification key, if any.
    if [ -e ${WORKDIR}/artifact-verify-key.pem ]; then
        if [ -n "${MENDER_ARTIFACT_VERIFY_KEY}" ]; then
            bbfatal "You can not specify both MENDER_ARTIFACT_VERIFY_KEY and have artifact-verify-key.pem in SRC_URI."
        fi
        install -m 0444 ${WORKDIR}/artifact-verify-key.pem ${D}${sysconfdir}/mender
    elif [ -n "${MENDER_ARTIFACT_VERIFY_KEY}" ]; then
        install -m 0444 "${MENDER_ARTIFACT_VERIFY_KEY}" ${D}${sysconfdir}/mender/artifact-verify-key.pem
    fi

    # Setup blacklist to ensure udev does not automatically mount Mender managed partitions
    install -d ${D}${sysconfdir}/udev/mount.blacklist.d
    echo ${MENDER_ROOTFS_PART_A} > ${D}${sysconfdir}/udev/mount.blacklist.d/mender
    echo ${MENDER_ROOTFS_PART_B} >> ${D}${sysconfdir}/udev/mount.blacklist.d/mender
}

do_install:append:class-target:mender-image:mender-systemd() {
    install -d ${D}${systemd_unitdir}/system/
    install -m 644 ${WORKDIR}/mender-data-dir.service ${D}${systemd_unitdir}/system/mender-data-dir.service
    install -d -m 755 ${D}${systemd_unitdir}/system/${MENDER_CLIENT}.service.wants
    ln -sf ../mender-data-dir.service ${D}${systemd_unitdir}/system/${MENDER_CLIENT}.service.wants/mender-data-dir.service
}

do_install:append:class-target:mender-growfs-data:mender-systemd() {

    if ${@bb.utils.contains('MENDER_FEATURES', 'mender-partlabel', 'true', 'false', d)}; then
        sed -i "s#@MENDER_DATA_PART@#\$(blkid -L ${MENDER_DATA_PART_LABEL})#g" \
            ${WORKDIR}/mender-resize-data-part.sh.in
    elif ${@bb.utils.contains('MENDER_FEATURES', 'mender-partuuid', 'true', 'false', d)}; then
        sed -i "s#@MENDER_DATA_PART@#\$(blkid | grep 'PARTUUID=\"${@mender_get_partuuid_from_device(d, '${MENDER_DATA_PART}')}\"' | awk -F: '{ print \$1 }')#g" \
            ${WORKDIR}/mender-resize-data-part.sh.in
    else
        sed -i "s#@MENDER_DATA_PART@#${MENDER_DATA_PART}#g" \
            ${WORKDIR}/mender-resize-data-part.sh.in
    fi

    sed -i "s#@MENDER_DATA_PART_NUMBER@#${MENDER_DATA_PART_NUMBER}#g" \
        ${WORKDIR}/mender-resize-data-part.sh.in


    install -d ${D}/${bindir}/

    install -m 0755 ${WORKDIR}/mender-resize-data-part.sh.in \
        ${D}/${bindir}/mender-resize-data-part

    install -d ${D}/${systemd_unitdir}/system
    install -m 644 ${WORKDIR}/mender-grow-data.service ${D}/${systemd_unitdir}/system/
    install -m 644 ${WORKDIR}/mender-systemd-growfs-data.service ${D}/${systemd_unitdir}/system/

    install -d ${D}${systemd_unitdir}/system/data.mount.wants/
    ln -sf ../mender-grow-data.service ${D}${systemd_unitdir}/system/data.mount.wants/
    ln -sf ../mender-systemd-growfs-data.service ${D}${systemd_unitdir}/system/data.mount.wants/
}

do_install:append:class-target:mender-persist-systemd-machine-id() {
    install -m 644 ${WORKDIR}/mender-systemd-machine-id.service ${D}${systemd_unitdir}/system/
    install -d -m 755 ${D}${systemd_unitdir}/system/${MENDER_CLIENT}.service.wants
    ln -sf ../mender-systemd-machine-id.service ${D}${systemd_unitdir}/system/${MENDER_CLIENT}.service.wants/
    install -d -m 755 ${D}${bindir}
    install -m 755 ${WORKDIR}/mender-set-systemd-machine-id.sh ${D}${bindir}/
}

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
