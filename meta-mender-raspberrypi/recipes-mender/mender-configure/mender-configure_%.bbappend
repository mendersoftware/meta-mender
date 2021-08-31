do_install_append_rpi() {
    # Insert key.
    sed -i -e '1s/$/\n  "mender-demo-raspberrypi-led": "mmc0",/' ${D}/data/mender-configure/device-config.json
}
