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

FILES:${PN}:append:mender-testing-enabled = "                       \
    /data/etc/systemd/                                              \
    /data/etc/systemd/system/mender-updated.service.d/              \
    /data/etc/systemd/system/mender-updated.service.d/override.conf \
    /etc/systemd/system/mender-updated.service.d/override.conf      \
"

# # Create an override.conf systemd file for the mender-updated.service file
do_install:append:mender-systemd:mender-testing-enabled() {
    mkdir -p ${D}/data/etc/systemd/system/mender-updated.service.d/
    mkdir -p ${D}/etc/systemd/system/mender-updated.service.d
    touch ${D}/data/etc/systemd/system/mender-updated.service.d/override.conf

    # NOTE: We use a relative path, as bitbake runs systemctl interactively
    # during build, and the global /data/etc/systemd/... does not exist on your
    # system ofc
    ln -s ../../../../data/etc/systemd/system/mender-updated.service.d/override.conf ${D}/etc/systemd/system/mender-updated.service.d/override.conf
}

do_compile:prepend() {
    if ${@bb.utils.contains('MENDER_FEATURES', 'mender-testing-enabled', 'false', 'true', d)}; then
        bbwarn "You are missing mender-testing-enabled feature for mender-ci layer to work properly"
    fi
}
