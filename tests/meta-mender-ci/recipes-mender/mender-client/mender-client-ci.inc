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
        sed -ri "s|ExecStart=(.*?) *daemon|ExecStart=\1 --log-level ${MENDER_CI_LOGLEVEL} daemon|" \
            ${D}/${systemd_unitdir}/system/${MENDER_CLIENT}.service
    fi
}

do_compile:prepend() {
    if ${@bb.utils.contains('MENDER_FEATURES', 'mender-testing-enabled', 'false', 'true', d)}; then
        bbwarn "You are missing mender-testing-enabled feature for mender-ci layer to work properly"
    fi
}
