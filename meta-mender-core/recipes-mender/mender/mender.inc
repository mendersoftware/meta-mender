DESCRIPTION = "Mender tool for doing OTA software updates."
HOMEPAGE = "https://mender.io"

def cert_location_if_server_crt_in(src_uri, d):
    for src in src_uri.split():
        if src.endswith("/server.crt"):
            return "%s/mender/server.crt" % d.getVar('sysconfdir')
    return ""

MENDER_SERVER_URL ?= "https://docker.mender.io"
MENDER_CERT_LOCATION ??= "${@cert_location_if_server_crt_in('${SRC_URI}', d)}"
# Tenant token
MENDER_TENANT_TOKEN ?= "dummy"
SYSTEMD_AUTO_ENABLE ?= "enable"
MENDER_UPDATE_POLL_INTERVAL_SECONDS ?= "1800"
MENDER_INVENTORY_POLL_INTERVAL_SECONDS ?= "1800"
MENDER_RETRY_POLL_INTERVAL_SECONDS ?= "300"

S = "${WORKDIR}/git"
B = "${WORKDIR}/build"

inherit go

inherit systemd

SYSTEMD_SERVICE_${PN} = "mender.service"
FILES_${PN} += "${systemd_unitdir}/system/mender.service \
                ${sysconfdir}/mender.conf \
                /data/mender/device_type \
                ${sysconfdir}/udev/mount.blacklist.d/mender \
               "

SRC_URI_append_mender-image_mender-systemd = " file://mender-data-dir.service"
SRC_URI_append_mender-persist-systemd-machine-id = " file://mender-systemd-machine-id.service \
                                                     file://mender-set-systemd-machine-id.sh"
FILES_${PN}_append_mender-image_mender-systemd = " ${systemd_unitdir}/system/mender-data-dir.service \
                                                   ${systemd_unitdir}/system/mender.service.wants/mender-data-dir.service"
FILES_${PN}_append_mender-persist-systemd-machine-id = " ${systemd_unitdir}/system/mender-systemd-machine-id.service \
                                                         ${systemd_unitdir}/system/mender.service.wants/mender-systemd-machine-id.service \
                                                         ${bindir}/mender-set-systemd-machine-id.sh"

# Go binaries produce unexpected effects that the Yocto QA mechanism doesn't
# like. We disable those checks here.
INSANE_SKIP_${PN} = "ldflags textrel"

GO_IMPORT = "github.com/mendersoftware/mender"

PACKAGECONFIG_append = "${@bb.utils.contains('DISTRO_FEATURES', 'mender-install', ' mender-install', '', d)}"
PACKAGECONFIG_append = "${@bb.utils.contains('DISTRO_FEATURES', 'mender-uboot', ' u-boot', '', d)}"
PACKAGECONFIG_append = "${@bb.utils.contains('DISTRO_FEATURES', 'mender-grub', ' grub', '', d)}"

PACKAGECONFIG[mender-install] = ",,,mender-artifact-info ca-certificates"
PACKAGECONFIG[u-boot] = ",,,u-boot-fw-utils"
PACKAGECONFIG[grub] = ",,,grub-editenv grub-mender-grubenv"
# The docker module depends on bash, and of course on docker. However, docker is
# a very large requirement, which we will not mandate. Bash however, we require,
# because otherwise the Yocto QA checks will complain.
PACKAGECONFIG[modules] = ",,,bash"

do_compile() {
    GOPATH="${B}:${S}"
    export GOPATH
    PATH="${B}/bin:$PATH"
    export PATH

    DEFAULT_CERT_MD5="1fba17436027eb1f5ceff4af9a63c9c2"

    if [ "$(md5sum ${WORKDIR}/server.crt | awk '{ print $1 }')" = $DEFAULT_CERT_MD5 ]; then
        bbwarn "You are building with the default server certificate, which is not intended for production use"
    fi

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

python do_prepare_mender_conf() {
    import json

    # If a mender.conf has been provided in SRC_URI, merge this with the
    # settings we generate. The settings specified by variables take precedence.
    src_conf = os.path.join(d.getVar("WORKDIR"), "mender.conf")
    if os.path.exists(src_conf):
        bb.debug(1, "mender.conf already present in ${WORKDIR}, merging with generated settings.")
        fd = open(src_conf)
        conf = json.load(fd)
        fd.close()
    else:
        bb.debug(1, "mender.conf not present in ${WORKDIR}, generating a new one.")
        conf = {}

    def conf_maybe_add(key, value, getvar, integer):
        if getvar:
            warn_str = "variable '%s'" % value
            value = d.getVar(value)
        else:
            warn_str = "automatically provided settings"
        if value is not None and value != "":
            if conf.get(key) is not None and conf[key] != value:
                bb.warn("Configuration key '%s', found in mender.conf, conflicts with %s. Choosing the latter." % (key, warn_str))
            if integer:
                conf[key] = int(value)
            else:
                conf[key] = value

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
    conf_maybe_add("ServerCertificate", "MENDER_CERT_LOCATION", getvar=True, integer=False)
    conf_maybe_add("ServerURL", "MENDER_SERVER_URL", getvar=True, integer=False)
    conf_maybe_add("UpdatePollIntervalSeconds", "MENDER_UPDATE_POLL_INTERVAL_SECONDS", getvar=True, integer=True)

    # Tenant-token is optional, but falls back to a default-value set in config.go
    conf_maybe_add("TenantToken", "MENDER_TENANT_TOKEN", getvar=True, integer=False)

    dst_conf = os.path.join(d.getVar("B"), "mender.conf")
    fd = open(dst_conf, "w")
    json.dump(conf, fd, indent=4, sort_keys=True)
    fd.close()
}
addtask do_prepare_mender_conf after do_compile before do_install
do_prepare_mender_conf[vardeps] = " \
    MENDER_ARTIFACT_VERIFY_KEY \
    MENDER_CERT_LOCATION \
    MENDER_INVENTORY_POLL_INTERVAL_SECONDS \
    MENDER_RETRY_POLL_INTERVAL_SECONDS \
    MENDER_ROOTFS_PART_A \
    MENDER_ROOTFS_PART_B \
    MENDER_SERVER_URL \
    MENDER_TENANT_TOKEN \
    MENDER_UPDATE_POLL_INTERVAL_SECONDS \
"

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
    install -m 0644 ${B}/mender.conf ${D}/${sysconfdir}/mender

    #install server certificate
    if [ -f ${WORKDIR}/server.crt ]; then
        install -m 0755 -d $(dirname ${D}${MENDER_CERT_LOCATION})
        install -m 0444 ${WORKDIR}/server.crt ${D}${MENDER_CERT_LOCATION}
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

do_install_append_mender-image_mender-systemd() {
    install -m 644 ${WORKDIR}/mender-data-dir.service ${D}${systemd_unitdir}/system/
    install -d -m 755 ${D}${systemd_unitdir}/system/mender.service.wants
    ln -sf ../mender-data-dir.service ${D}${systemd_unitdir}/system/mender.service.wants/
}

do_install_append_mender-persist-systemd-machine-id() {
    install -m 644 ${WORKDIR}/mender-systemd-machine-id.service ${D}${systemd_unitdir}/system/
    install -d -m 755 ${D}${systemd_unitdir}/system/mender.service.wants
    ln -sf ../mender-systemd-machine-id.service ${D}${systemd_unitdir}/system/mender.service.wants/
    install -d -m 755 ${D}${bindir}
    install -m 755 ${WORKDIR}/mender-set-systemd-machine-id.sh ${D}${bindir}
}
