python do_prepare_docker_daemon_conf() {
    import json

    data_root = d.getVar("MENDER_DOCKER_DATA_ROOT")
    if not data_root:
        return

    file = os.path.join(d.getVar("WORKDIR"), "daemon.json")

    if os.path.exists(file):
        with open(file, "r") as fd:
            data = json.load(fd)
    else:
        data = {}

    data["data-root"] = data_root
    with open(file, "w") as fd:
        json.dump(data, fd, indent=2)
}

addtask do_prepare_docker_daemon_conf after do_compile before do_install

do_install:append:mender-image() {
    if [ -n "${MENDER_DOCKER_DATA_ROOT}" ]; then
        install -d ${D}${sysconfdir}/docker
        install -m 0644 ${WORKDIR}/daemon.json ${D}${sysconfdir}/docker/daemon.json
    fi
}

FILES:${PN}:append:mender-image = "${@' ${sysconfdir}/docker/daemon.json' if d.getVar('MENDER_DOCKER_DATA_ROOT') else ''}"
