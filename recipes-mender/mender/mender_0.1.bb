DESCRIPTION = "Mender tool for doing OTA software updates."
HOMEPAGE = "https://mender.io"

MENDER_SERVER_URL ?= "https://mender-api-gateway"
MENDER_CERT_LOCATION ?= "${sysconfdir}/mender/server.crt"
# Tenant token
MENDER_TENANT_TOKEN ?= "dummy"
SYSTEMD_AUTO_ENABLE ?= "disable"

#From oe-meta-go (https://github.com/mem/oe-meta-go)
DEPENDS = "go-cross godep lmdb-go"
S = "${WORKDIR}/git"
B = "${WORKDIR}/build"

inherit go

SRC_URI = "git://github.com/mendersoftware/mender;protocol=https \
           file://mender.service \
           file://mender.conf \
           file://server.crt \
          "

SRCREV = "${AUTOREV}"
PVBASE := "${PV}"
PV = "${PVBASE}+git${SRCPV}"

# DO NOT change the checksum here without make sure that ALL licenses (including
# dependencies) are included in the LICENSE variable below.
LIC_FILES_CHKSUM = "file://LIC_FILES_CHKSUM.sha256;md5=3251d4712ab2812c702ff7505d215ea3"
LICENSE = "Apache-2.0 & BSD-2-Clause & BSD-3-Clause & MIT & OLDAP-2.8"

inherit systemd

SYSTEMD_SERVICE_${PN} = "mender.service"
FILES_${PN} += "${systemd_unitdir}/system/mender.service \
                ${sysconfdir}/mender.conf \
               "
export CGO_ENABLED = "1"
export CGO_CFLAGS = "${CFLAGS} --sysroot=${STAGING_DIR_TARGET}"
export CGO_LDFLAGS = "${LDFLAGS} --sysroot=${STAGING_DIR_TARGET}"

# Go binaries produce unexpected effects that the Yocto QA mechanism doesn't
# like. We disable those checks here.
INSANE_SKIP_${PN} = "ldflags"

do_compile() {
  GOPATH="${B}:${S}:${STAGING_LIBDIR}/${TARGET_SYS}/go"
  export GOPATH
  PATH="${B}/bin:$PATH"
  export PATH

  # mender is using vendored dependencies, any 3rd party libraries go to into
  # /vendor directory inside mender source tree. In order for `go build` to pick
  # up vendored deps from our source tree, the mender source tree itself must be
  # located inside $GOPATH/src, for instance $GOPATH/src/mender
  #
  # recreate temporary $GOPATH/src/mender structure and link our source tree
  mkdir -p ${B}/src
  test -e ${B}/src/mender || ln -s ${S} ${B}/src/mender
  cd ${B}/src/mender

  # run verbose build, we should see which dependencies are pulled in
  oe_runmake V=1 install

  #prepare Mender configuration file
  cp ${WORKDIR}/mender.conf ${B}
  sed -i -e 's#[@]MENDER_SERVER_URL[@]#${MENDER_SERVER_URL}#' ${B}/mender.conf
  sed -i -e 's#[@]MENDER_CERT_LOCATION[@]#${MENDER_CERT_LOCATION}#' ${B}/mender.conf

  if [ -n "${MENDER_ROOTFS_PART_A}" ] && [ -n "${MENDER_ROOTFS_PART_B}" ]; then
    sed -i -e 's#[@]MENDER_ROOTFS_PART_A[@]#${MENDER_ROOTFS_PART_A}#' ${B}/mender.conf
    sed -i -e 's#[@]MENDER_ROOTFS_PART_B[@]#${MENDER_ROOTFS_PART_B}#' ${B}/mender.conf
  fi

  echo "${MENDER_TENANT_TOKEN}" > ${B}/tenant.conf
}

do_install() {
  install -d ${D}/${bindir}

  GOOS=$(eval $(go env) && echo $GOOS)
  GOARCH=$(eval $(go env) && echo $GOARCH)
  # mender is picked up from our fake GOPATH=${B}/bin; because go build is so
  # consistent, if it's a cross compilation build, binaries will be in
  # ${GOPATH}/bin/${GOOS}_${GOARCH}, howver if it's not, the binaries are in
  # ${GOPATH}/bin; handle cross compiled case only
  install -t ${D}/${bindir} -m 0755 \
          ${B}/bin/${GOOS}_${GOARCH}/mender \
          ${S}/support/mender-device-identity

  install -d ${D}/${systemd_unitdir}/system
  install -m 0644 ${WORKDIR}/mender.service ${D}/${systemd_unitdir}/system

  #install configuration
  install -d ${D}/${sysconfdir}/mender
  install -m 0644 ${B}/mender.conf ${D}/${sysconfdir}/mender
  install -m 0600 ${B}/tenant.conf ${D}/${sysconfdir}/mender

  #install server certificate
  install -m 0444 ${WORKDIR}/server.crt ${D}/${sysconfdir}/mender

  install -d ${D}/${localstatedir}/lib/mender
}

do_install_append_menderimage() {
  # symlink /var/lib/mender to /data/mender
  rm -rf ${D}/${localstatedir}/lib/mender
  ln -s /data/mender ${D}/${localstatedir}/lib/mender
}
