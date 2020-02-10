# Build file for the old makefile, where the install target only installs the
# binary.

SRC_URI_append = " file://mender.service \
                 "

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

    echo "device_type=${MENDER_DEVICE_TYPE}" > ${B}/device_type
}

do_install() {
    install -d ${D}/${bindir}

    GOOS=$(eval $(${GO} env) && echo $GOOS)
    GOARCH=$(eval $(${GO} env) && echo $GOARCH)
    if [ "${BUILD_ARCH}" = "${HOST_ARCH}" ]; then
        BUILD_BIN_FOLDER=${B}/bin
    else
        BUILD_BIN_FOLDER=${B}/bin/${GOOS}_${GOARCH}
    fi
    # mender is picked up from our fake GOPATH=${B}/bin; because go build is so
    # consistent, if it's a cross compilation build, binaries will be in
    # ${GOPATH}/bin/${GOOS}_${GOARCH}, howver if it's not, the binaries are in
    # ${GOPATH}/bin; handle cross compiled case only
    install -t ${D}/${bindir} -m 0755 \
            ${BUILD_BIN_FOLDER}/mender

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
