# Produce custom level logs when MENDER_CI_LOGLEVEL is enabled
do_install_append_class-target_mender-image_mender-systemd() {
    if ${@'true' if d.getVar('MENDER_CI_LOGLEVEL') else 'false'}; then
        local logging_level=""
        if [ "${MENDER_CI_LOGLEVEL}" = "debug" ]; then
            logging_level="DEBUG"
        elif [ "${MENDER_CI_LOGLEVEL}" = "trace" ]; then
            logging_level="TRACE"
        fi

        if [ -n "$logging_level" ]; then
            sed -i "s|CONFIG_LOG_LEVEL=.*|CONFIG_LOG_LEVEL=${logging_level}|" \
                ${D}/${datadir}/mender-monitor/config/config.sh
        else
            bbwarn "Unknown MENDER_CI_LOGLEVEL ${MENDER_CI_LOGLEVEL} for mender-monitor. Ignoring."
        fi
    fi
}
