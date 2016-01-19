do_compile() {
  ## Setting `$GOBIN` doesn't do any good, looks like it ends up copying binaries there.
  export GOROOT_FINAL="${SYSROOT}${nonarch_libdir}/${PN}-${PV}"

  setup_go_arch

  export CGO_ENABLED="1"
  ## TODO: consider setting GO_EXTLINK_ENABLED

  ## You'd expect this to be the correct values for building Go for the
  ## host. Turns out that depending on "gcc" does not provide enough of
  ## build environment for this to work, so we fall back on relying on
  ## on the host's toolchain and development environment (which
  ## messes up with a situation that relies heavily on sstate).
  #
  # export CC="${BUILD_CC}"
  # export CC_FOR_TARGET="${BUILD_CC} ${TARGET_CC_ARCH} --sysroot=${STAGING_DIR_NATIVE}"
  # export CXX_FOR_TARGET="${BUILD_CXX} ${TARGET_CC_ARCH} --sysroot=${STAGING_DIR_NATIVE}"
  # export GO_CCFLAGS="${BUILD_OPTIMIZATION}"
  # export GO_LDFLAGS="${BUILD_LDFLAGS}"

  cd src && bash -x ./make.bash

  # log the resulting environment
  env "GOROOT=${WORKDIR}/go-${PV}/go" "${WORKDIR}/go-${PV}/go/bin/go" env
}

