SYSTEMD_AUTO_ENABLE = "disable"

# Add these empty functions to prevent ptest from running for the acceptance
# tests. They add significant running time to each test, and it is enough to
# test them once in the main build.
do_compile_ptest_base() {
}
do_install_ptest_base() {
}

# Produce custom level logs when MENDER_CI_LOGLEVEL is enabled
do_install:append:class-target:mender-image:mender-systemd() {
    if ${@'true' if d.getVar('MENDER_CI_LOGLEVEL') else 'false'}; then
        sed -i "s|ExecStart=.*|ExecStart=/usr/bin/${MENDER_CLIENT} --log-level ${MENDER_CI_LOGLEVEL} daemon|" \
            ${D}/${systemd_unitdir}/system/${MENDER_CLIENT}.service
    fi
}
