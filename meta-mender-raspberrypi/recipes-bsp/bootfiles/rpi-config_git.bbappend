
do_deploy_append() {
    # Recently the default clock rate for uart changed to 48 MHz. This is
    # setup by boot firmware. This update has not been aligned in u-boot nor in
    # Linux yet.
    #
    # Override the default with the previous default which is 3 MHz. This
    # workaround can be dropped once the configuration aligns upstream.
    sed -i '/#init_uart_clock/ c\init_uart_clock=3000000' ${DEPLOYDIR}/bcm2835-bootfiles/config.txt
}
