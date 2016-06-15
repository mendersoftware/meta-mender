DESCRIPTION = "Mender tool for doing OTA software updates."
HOMEPAGE = "https://mender.io/"

MENDER_SERVER_URL ?= "https://mender.io"
MENDER_CERT_LOCATION ?= ""

#From oe-meta-go (https://github.com/mem/oe-meta-go)
DEPENDS = "go-cross godep"
S = "${WORKDIR}/git"

inherit go

SRC_URI = "git://github.com/mendersoftware/mender;protocol=https \
           file://mender.service \
           file://mender.conf \
           file://server.crt \
          "

SRCREV = "${AUTOREV}"
PVBASE := "${PV}"
PV = "${PVBASE}+git${SRCPV}"

LICENSE = "Apache-2.0"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/Apache-2.0;md5=89aea4e17d99a7cacdbeed46a0096b10"

inherit systemd

SYSTEMD_SERVICE_${PN} = "mender.service"
FILES_${PN} += "${systemd_unitdir}/system/mender.service \
                ${sysconfdir}/mender.conf \
               "

do_configure() {
  # Move/copy all file:// URIs into WORKDIR. We need to manually move/copy them
  # because externalsrc builds do not automatically fetch local files from the
  # bb recipe, and we need to put them in WORKDIR because we should not copy
  # them into S if it is external.

  # Bitbake quoting rules mean we need to make an intermediate variable here.
  SRC_URI='${SRC_URI}'
  for file in $SRC_URI; do
    case $file in
      file://)
        if [ -n "${EXTERNALSRC}" ]; then
          for path in ${FILESPATH}; do
            if [ -e $path/$file ]; then
              cp -r $path/$file ${WORKDIR}
              break
            fi
          done
        else
          mv `basename $file` ${WORKDIR}
        fi
        ;;
      *)
        continue
        ;;
    esac
  done
}

do_compile() {
  GOPATH="${B}:${S}"
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

  #install server certificate
  install -m 0444 ${WORKDIR}/server.crt ${D}/${sysconfdir}/mender
}
