MENDER_DEMO_HOST_IP_ADDRESS ?= ""

do_install_append() {
    if [ -n "${MENDER_DEMO_HOST_IP_ADDRESS}" ]; then
        echo "${MENDER_DEMO_HOST_IP_ADDRESS} docker.mender.io s3.docker.mender.io" >> ${D}${sysconfdir}/hosts
    fi
}
