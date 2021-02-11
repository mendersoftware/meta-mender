
do_compile_append() {
    cat > ${B}/apply-device-config << END
#!/bin/sh
exit 0
END
}

do_install_append() {
    install -d ${D}${libdir}/mender-configure
    install -m 0755 -t ${D}${libdir}/mender-configure ${B}/apply-device-config
}

FILES_${PN} += " \
    ${libdir}/mender-configure/apply-device-config \
"
