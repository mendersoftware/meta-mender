do_install() {
  install -d "${D}${bindir}" "${D}${GOROOT_FINAL}"
  tar -C "${WORKDIR}/go-${PV}/go" -cf - bin lib src pkg test |
  tar -C "${D}${GOROOT_FINAL}" -xf -
  mv "${D}${GOROOT_FINAL}/bin/"* "${D}${bindir}/"

  for t in gcc g++ ; do
    cat > ${D}${GOROOT_FINAL}/bin/${TARGET_PREFIX}${t} <<EOT
#!/bin/sh
exec ${TARGET_PREFIX}${t} ${TARGET_CC_ARCH} --sysroot=${STAGING_DIR_TARGET} "\$@"
EOT
    chmod +x ${D}${GOROOT_FINAL}/bin/${TARGET_PREFIX}${t}
  done
}

INHIBIT_SYSROOT_STRIP = "1"
