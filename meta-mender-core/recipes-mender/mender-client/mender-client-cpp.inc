inherit mender-licensing

BBCLASSEXTEND = "native"
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

_MENDER_WATCHDOG_DEFAULT_TIMEOUT_SEC ?= "86400"
MENDER_WATCHDOG_SEC ?= "${@max(d.getVar('MENDER_UPDATE_POLL_INTERVAL_SECONDS'), d.getVar('_MENDER_WATCHDOG_DEFAULT_TIMEOUT_SEC'))}"

PACKAGES =+ "mender-auth mender-update mender-config mender-auth-dev"

RDEPENDS:mender-auth += "mender-config"

RDEPENDS:mender-update += "mender-auth mender-config"
RRECOMMENDS:mender-update += "mender-flash"

# rootfs-image module uses jq to parse the config file, but it is able to fall
# back to line based parsing, which is less resilient.
RRECOMMENDS:mender-update:append = "${@bb.utils.contains('PACKAGECONFIG', 'modules', ' jq', '', d)}"

SYSTEMD_SERVICE:mender-update = "mender-updated.service"
SYSTEMD_SERVICE:mender-auth = "mender-authd.service"
SYSTEMD_PACKAGES = "mender-update mender-auth"

MENDER_CLIENT ?= "mender-updated"

# Don't download the googletest source in Mender CMakefiles.txt
EXTRA_OECMAKE:append = " -DMENDER_DOWNLOAD_GTEST=NO"

inherit cmake

DEPENDS += "lmdb googletest boost libarchive dbus"
RDEPENDS:mender-auth:append = " boost-filesystem dbus"
RDEPENDS:mender-update:append = " boost-filesystem libarchive lmdb dbus"

RDEPENDS:mender-update:append:mender-growfs-data:mender-systemd = " parted util-linux-fdisk"
RDEPENDS:mender-update:append:mender-growfs-data:mender-systemd:mender-partlabel = " util-linux-blkid"
RDEPENDS:mender-update:append:mender-growfs-data:mender-systemd:mender-partuuid = " util-linux-blkid"

_MENDER_PACKAGECONFIG_DEFAULT = "modules inventory-network-scripts"
PACKAGECONFIG ?= "${_MENDER_PACKAGECONFIG_DEFAULT}"

PACKAGECONFIG:append:class-target = "${@bb.utils.contains('MENDER_FEATURES', 'mender-uboot', ' u-boot', '', d)}"
PACKAGECONFIG:append:class-target = "${@bb.utils.contains('MENDER_FEATURES', 'mender-grub', ' grub', '', d)}"

RRECOMMENDS:mender-auth:append = " ca-certificates"

PACKAGECONFIG[u-boot] = ",,,"
RDEPENDS:mender-update:append = "${@bb.utils.contains('PACKAGECONFIG', 'u-boot', ' libubootenv-bin', '', d)}"
PACKAGECONFIG[grub] = ",,,"
RDEPENDS:mender-update:append = "${@bb.utils.contains('PACKAGECONFIG', 'grub', ' grub-editenv grub-mender-grubenv', '', d)}"

# The docker module depends on bash, and of course on docker. However, docker is
# a very large requirement, which we will not mandate. Bash however, we require,
# because otherwise the Yocto QA checks will complain.
PACKAGECONFIG[modules] = ",,,"
RDEPENDS:mender-update:append = "${@bb.utils.contains('PACKAGECONFIG', 'modules', ' bash', '', d)}"

PACKAGECONFIG[inventory-network-scripts] = ",,,"

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

FILES:mender-update:append:mender-image:mender-systemd = " \
    ${systemd_unitdir}/system/mender-data-dir.service \
    ${systemd_unitdir}/system/${MENDER_CLIENT}.service.wants/mender-data-dir.service \
"

FILES:mender-update:append:mender-growfs-data:mender-systemd = " \
    ${bindir}/mender-resize-data-part \
    ${systemd_unitdir}/system/mender-grow-data.service \
    ${systemd_unitdir}/system/mender-systemd-growfs-data.service \
    ${systemd_unitdir}/system/data.mount.wants/mender-grow-data.service \
    ${systemd_unitdir}/system/data.mount.wants/mender-systemd-growfs-data.service \
"

FILES:mender-update:append:mender-persist-systemd-machine-id = " \
    ${systemd_unitdir}/system/mender-systemd-machine-id.service \
    ${systemd_unitdir}/system/${MENDER_CLIENT}.service.wants/mender-systemd-machine-id.service \
    ${bindir}/mender-set-systemd-machine-id.sh \
"

FILES:mender-config += "\
    ${localstatedir}/lib/mender \
    ${sysconfdir}/mender/mender.conf \
    ${_MENDER_PERSISTENT_DIR}/device_type \
    ${_MENDER_PERSISTENT_DIR}/mender.conf \
"

FILES:mender-update += "\
    ${bindir}/mender-update \
    ${datadir}/mender/inventory \
    ${datadir}/mender/inventory/mender-inventory-bootloader-integration \
    ${datadir}/mender/inventory/mender-inventory-hostinfo \
    ${datadir}/mender/inventory/mender-inventory-network \
    ${datadir}/mender/inventory/mender-inventory-os \
    ${datadir}/mender/inventory/mender-inventory-rootfs-type \
    ${sysconfdir}/udev/mount.blacklist.d/mender \
"
FILES:mender-update:append = "${@bb.utils.contains('PACKAGECONFIG', 'modules', ' ${datadir}/mender/modules', '', d)}"

FILES:mender-auth += "\
    ${bindir}/mender-auth \
    ${datadir}/mender/identity \
    ${datadir}/mender/identity/mender-device-identity \
    ${datadir}/dbus-1/system.d/io.mender.AuthenticationManager.conf \
"

FILES:mender-auth-dev += "\
    ${datadir}/dbus-1/interfaces/io.mender.Authentication1.xml \
"

FILES:mender-update += "\
    ${systemd_unitdir}/system/mender-updated.service \
"

FILES:mender-auth += "\
    ${systemd_unitdir}/system/mender-authd.service \
"

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

do_install() {
    DESTDIR='${D}' cmake_runcmake_build --target install-bin
    DESTDIR='${D}' cmake_runcmake_build --target install-identity-scripts
    DESTDIR='${D}' cmake_runcmake_build --target install-systemd
    if ${@bb.utils.contains('PACKAGECONFIG', 'modules', 'true', 'false', d)}; then
        DESTDIR='${D}' cmake_runcmake_build --target install-modules
    fi

    # install inventory scripts
    DESTDIR='${D}' cmake_runcmake_build --target install-inventory-scripts
    if ${@bb.utils.contains('PACKAGECONFIG', 'inventory-network-scripts', 'true', 'false', d)}; then
        DESTDIR='${D}' cmake_runcmake_build --target install-inventory-network-scripts
    fi

    # install dbus files
    DESTDIR='${D}' cmake_runcmake_build --target install-dbus
}

do_install:append:class-target:mender-systemd() {
    sed -i "s/WatchdogSec=86400/WatchdogSec=${MENDER_WATCHDOG_SEC}/" ${D}${systemd_unitdir}/system/mender-updated.service
}

# Native overrides, installing scripts for package mender-modules-gen
EXTRA_OECMAKE:append:class-native = " -DMENDER_NO_BUILD=1"

do_install:class-native() {
    DESTDIR='${D}' cmake_runcmake_build --target install-modules-gen
}
