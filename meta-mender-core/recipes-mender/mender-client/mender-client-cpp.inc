require mender-client.inc

DESCRIPTION = "Mender tool for doing OTA software updates."
HOMEPAGE = "https://mender.io"

PACKAGES =+ "mender-auth mender-update mender-config"

RDEPENDS:mender-auth = "mender-config"

RPROVIDES:mender-update = "mender-client"
RDEPENDS:mender-update = "mender mender-auth mender-config"

# rootfs-image module uses jq to parse the config file, but it is able to fall
# back to line based parsing, which is less resilient.
RRECOMMENDS:mender-update:append = "${@bb.utils.contains('PACKAGECONFIG', 'modules', ' jq', '', d)}"

PROVIDES += "mender-auth mender-update"

SYSTEMD_SERVICE:mender-update = "mender-updated.service"
SYSTEMD_SERVICE:mender-auth = "mender-authd.service"

MENDER_CLIENT ?= "mender-updated"

# Don't download the googletest source in Mender CMakefiles.txt
EXTRA_OECMAKE:append = " -DMENDER_DOWNLOAD_GTEST=NO"

inherit cmake

RDEPENDS:mender-update:append:mender-growfs-data:mender-systemd = " parted util-linux-fdisk"
RDEPENDS:mender-update:append:mender-growfs-data:mender-systemd:mender-partlabel = " util-linux-blkid"
RDEPENDS:mender-update:append:mender-growfs-data:mender-systemd:mender-partuuid = " util-linux-blkid"


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
    ${datadir}/mender/modules/v3/deb \
    ${datadir}/mender/modules/v3/directory \
    ${datadir}/mender/modules/v3/docker \
    ${datadir}/mender/modules/v3/rpm \
    ${datadir}/mender/modules/v3/script \
    ${datadir}/mender/modules/v3/single-file \
    ${sysconfdir}/udev/mount.blacklist.d/mender \
    ${datadir}/dbus-1/interface \
    ${datadir}/dbus-1/system.d/io.mender.UpdateManager.conf \
    ${datadir}/dbus-1/interface/io.mender.Update1.xml \
"

FILES:mender-auth += "\
    ${bindir}/mender-auth \
    ${datadir}/mender/identity \
    ${datadir}/mender/identity/mender-device-identity \
    ${datadir}/dbus-1/interface \
    ${datadir}/dbus-1/interface/io.mender.Authentication1.xml \
    ${datadir}/dbus-1/system.d/io.mender.AuthenticationManager.conf \
"

FILES:mender-auth-dev += " \
    ${datadir}/dbus-1/interface \
"

FILES:mender-update += "\
    ${systemd_unitdir}/system/mender-updated.service \
"

FILES:mender-auth += "\
    ${systemd_unitdir}/system/mender-authd.service \
"

DEPENDS += "lmdb googletest boost libarchive"
RDEPENDS:mender-auth:append = " boost-filesystem"
RDEPENDS:mender-update:append = " boost-filesystem libarchive lmdb"

# Native overrides, installing scripts for package mender-modules-gen
do_configure:class-native() {
    true
}

do_compile:class-native() {
    true
}

do_install:class-native() {
    true
}
