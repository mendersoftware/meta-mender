DESCRIPTION = "Mender tool for doing OTA software updates."
HOMEPAGE = "https://mender.io"

def cert_location_if_server_crt_in(src_uri, d):
    for src in src_uri.split():
        if src.endswith("/server.crt"):
            return "%s/mender/server.crt" % d.getVar('sysconfdir')
    return ""

MENDER_SERVER_URL ?= "https://docker.mender.io"
MENDER_CERT_LOCATION ?= "${@cert_location_if_server_crt_in('${SRC_URI}', d)}"
# Tenant token
MENDER_TENANT_TOKEN ?= "dummy"
SYSTEMD_AUTO_ENABLE ?= "enable"
MENDER_UPDATE_POLL_INTERVAL_SECONDS ?= "1800"
MENDER_INVENTORY_POLL_INTERVAL_SECONDS ?= "1800"
MENDER_RETRY_POLL_INTERVAL_SECONDS ?= "300"

S = "${WORKDIR}/git"
B = "${WORKDIR}/build"

inherit go

SRC_URI_append = " file://mender.service \
                 "

inherit systemd

SYSTEMD_SERVICE_${PN} = "mender.service"
FILES_${PN} += "${systemd_unitdir}/system/mender.service \
                ${sysconfdir}/mender.conf \
               "

# Go binaries produce unexpected effects that the Yocto QA mechanism doesn't
# like. We disable those checks here.
INSANE_SKIP_${PN} = "ldflags"

GO_IMPORT = "github.com/mendersoftware/mender"

PACKAGECONFIG_append = "${@bb.utils.contains('DISTRO_FEATURES', 'mender-install', ' mender-install', '', d)}"
PACKAGECONFIG_append = "${@bb.utils.contains('DISTRO_FEATURES', 'mender-uboot', ' u-boot', '', d)}"

PACKAGECONFIG[mender-install] = ",,,mender-artifact-info ca-certificates"
PACKAGECONFIG[u-boot] = ",,u-boot-fw-utils,u-boot-fw-utils"

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
    oe_runmake V=1 install

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

    def conf_maybe_add(key, value, integer):
        if value is not None and value != "":
            if integer:
                conf[key] = int(value)
            else:
                conf[key] = value

    key_in_src_uri = os.path.exists(os.path.join(d.getVar("WORKDIR"), "artifact-verify-key.pem"))
    key_in_var = d.getVar("MENDER_ARTIFACT_VERIFY_KEY") not in [None, ""]

    # Add new variable -> config assignments here.
    if key_in_src_uri or key_in_var:
        conf_maybe_add("ArtifactVerifyKey", "%s/mender/artifact-verify-key.pem" % d.getVar("sysconfdir"), integer=False)
    conf_maybe_add("InventoryPollIntervalSeconds", d.getVar("MENDER_INVENTORY_POLL_INTERVAL_SECONDS"), integer=True)
    # Mandatory variables - will always exist
    conf_maybe_add("RetryPollIntervalSeconds", d.getVar("MENDER_RETRY_POLL_INTERVAL_SECONDS"), integer=True)
    conf_maybe_add("RootfsPartA", d.getVar("MENDER_ROOTFS_PART_A"), integer=False)
    conf_maybe_add("RootfsPartB", d.getVar("MENDER_ROOTFS_PART_B"), integer=False)
    conf_maybe_add("ServerCertificate", d.getVar("MENDER_CERT_LOCATION"), integer=False)
    conf_maybe_add("ServerURL", d.getVar("MENDER_SERVER_URL"), integer=False)
    conf_maybe_add("UpdatePollIntervalSeconds", d.getVar("MENDER_UPDATE_POLL_INTERVAL_SECONDS"), integer=True)

    # Tenant-token is optional, but falls back to a default-value set in config.go
    conf_maybe_add("TenantToken", d.getVar("MENDER_TENANT_TOKEN"), integer=False)

    dst_conf = os.path.join(d.getVar("B"), "mender.conf")
    fd = open(dst_conf, "w")
    json.dump(conf, fd, indent=4, sort_keys=True)
    fd.close()
}
addtask do_prepare_mender_conf after do_compile before do_install

do_install() {
    install -d ${D}/${bindir}

    GOOS=$(eval $(${GO} env) && echo $GOOS)
    GOARCH=$(eval $(${GO} env) && echo $GOARCH)
    # mender is picked up from our fake GOPATH=${B}/bin; because go build is so
    # consistent, if it's a cross compilation build, binaries will be in
    # ${GOPATH}/bin/${GOOS}_${GOARCH}, howver if it's not, the binaries are in
    # ${GOPATH}/bin; handle cross compiled case only
    install -t ${D}/${bindir} -m 0755 \
            ${B}/bin/${GOOS}_${GOARCH}/mender

    install -d ${D}/${datadir}/mender/identity
    install -t ${D}/${datadir}/mender/identity -m 0755 \
            ${S}/src/${GO_IMPORT}/support/mender-device-identity

    # install example inventory tools
    install -d ${D}/${datadir}/mender/inventory
    install -t ${D}/${datadir}/mender/inventory -m 0755 \
            ${S}/src/${GO_IMPORT}/support/mender-inventory-*

    install -d ${D}/${systemd_unitdir}/system
    install -m 0644 ${WORKDIR}/mender.service ${D}/${systemd_unitdir}/system

    #install configuration
    install -d ${D}/${sysconfdir}/mender
    install -m 0644 ${B}/mender.conf ${D}/${sysconfdir}/mender

    #install server certificate
    if [ -f ${WORKDIR}/server.crt ]; then
        install -m 0444 ${WORKDIR}/server.crt ${D}/${sysconfdir}/mender
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
    fi
}
