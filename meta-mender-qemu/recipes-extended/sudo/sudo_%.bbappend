FILES:${PN} += "/data/usr"

do_install:append:qemux86-64 () {
    mkdir -p ${D}/data/usr/bin
    mv ${D}/usr/bin/sudo ${D}/data/usr/bin/
    ln -s /data/usr/bin/sudo ${D}/usr/bin/sudo
}

do_install:append_vexpress-qemu () {
    mkdir -p ${D}/data/usr/bin
    mv ${D}/usr/bin/sudo ${D}/data/usr/bin/
    ln -s /data/usr/bin/sudo ${D}/usr/bin/sudo
}

