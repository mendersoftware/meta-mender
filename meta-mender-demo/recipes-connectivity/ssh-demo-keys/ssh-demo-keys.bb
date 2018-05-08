LICENSE = "PD"

do_install() {
    # Refuse to do this on anything but QEMU, since it is so insecure.
    if [ "${MACHINE}" != "vexpress-qemu" ] && [ "${MACHINE}" != "vexpress-qemu-flash" ]; then
        bbfatal "${PN} should never be installed on anything but QEMU. It is INSECURE!"
    fi

    mkdir -p ${D}${sysconfdir}/ssh

    # Yocto doesn't provide ssh-keygen-native, so we'll just have to use the
    # platform one. Virtually everyone should have this though.

    /usr/bin/ssh-keygen -f ${D}${sysconfdir}/ssh/ssh_host_rsa_key -N '' -t rsa
    /usr/bin/ssh-keygen -f ${D}${sysconfdir}/ssh/ssh_host_ecdsa_key -N '' -t ecdsa
    /usr/bin/ssh-keygen -f ${D}${sysconfdir}/ssh/ssh_host_dsa_key -N '' -t dsa
    /usr/bin/ssh-keygen -f ${D}${sysconfdir}/ssh/ssh_host_ed25519_key -N '' -t ed25519
}
