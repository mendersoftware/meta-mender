DESCRIPTION = "Mender tool for doing OTA software updates."
HOMEPAGE = "https://mender.io"

MENDER_SERVER_URL ?= "https://docker.mender.io"
MENDER_CERT_LOCATION ?= "${sysconfdir}/mender/server.crt"
# Tenant token
MENDER_TENANT_TOKEN ?= "dummy"
SYSTEMD_AUTO_ENABLE ?= "enable"
MENDER_UPDATE_POLL_INTERVAL_SECONDS ?= "1800"
MENDER_INVENTORY_POLL_INTERVAL_SECONDS ?= "1800"
MENDER_RETRY_POLL_INTERVAL_SECONDS ?= "300"

S = "${WORKDIR}/git"
B = "${WORKDIR}/build"

inherit go

SRC_URI = "git://github.com/mendersoftware/mender;branch=stable;protocol=https \
           file://mender.service \
           file://mender.conf \
           file://server.crt \
          "

SRCREV = "${AUTOREV}"
PVBASE := "${PV}"
PV = "${PVBASE}+git${SRCPV}"

# DO NOT change the checksum here without make sure that ALL licenses (including
# dependencies) are included in the LICENSE variable below.
LIC_FILES_CHKSUM = "file://LIC_FILES_CHKSUM.sha256;md5=ec8e15a3ea20289732cca4a7ef643ef8"
LICENSE = "Apache-2.0 & BSD-2-Clause & BSD-3-Clause & MIT & OLDAP-2.8"

inherit systemd

SYSTEMD_SERVICE_${PN} = "mender.service"
FILES_${PN} += "${systemd_unitdir}/system/mender.service \
                ${sysconfdir}/mender.conf \
               "

# Go binaries produce unexpected effects that the Yocto QA mechanism doesn't
# like. We disable those checks here.
INSANE_SKIP_${PN} = "ldflags"

GO_IMPORT = "github.com/mendersoftware/mender"

PACKAGECONFIG[u-boot] = ",,,u-boot-fw-utils"

RDEPENDS_${PN} += " \
    mender-artifact-info \
    "

do_compile() {
  GOPATH="${B}:${S}"
  export GOPATH
  PATH="${B}/bin:$PATH"
  export PATH

  DEFAULT_CERT_MD5="e034532805e44b9125b443c32bbde581"

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

  #prepare Mender configuration file
  cp ${WORKDIR}/mender.conf ${B}
  sed -i -e 's#[@]MENDER_SERVER_URL[@]#${MENDER_SERVER_URL}#' ${B}/mender.conf
  sed -i -e 's#[@]MENDER_CERT_LOCATION[@]#${MENDER_CERT_LOCATION}#' ${B}/mender.conf
  sed -i -e 's#[@]MENDER_UPDATE_POLL_INTERVAL_SECONDS[@]#${MENDER_UPDATE_POLL_INTERVAL_SECONDS}#' ${B}/mender.conf
  sed -i -e 's#[@]MENDER_INVENTORY_POLL_INTERVAL_SECONDS[@]#${MENDER_INVENTORY_POLL_INTERVAL_SECONDS}#' ${B}/mender.conf
  sed -i -e 's#[@]MENDER_RETRY_POLL_INTERVAL_SECONDS[@]#${MENDER_RETRY_POLL_INTERVAL_SECONDS}#' ${B}/mender.conf

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
          ${B}/bin/${GOOS}_${GOARCH}/mender

  install -d ${D}/${datadir}/mender/identity
  install -t ${D}/${datadir}/mender/identity -m 0755 \
          ${S}/support/mender-device-identity

  # install example inventory tools
  install -d ${D}/${datadir}/mender/inventory
  install -t ${D}/${datadir}/mender/inventory -m 0755 \
          ${S}/support/mender-inventory-*

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
