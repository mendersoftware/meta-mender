SYSTEMD_AUTO_ENABLE = "disable"

# Add these empty functions to prevent ptest from running for the acceptance
# tests. They add significant running time to each test, and it is enough to
# test them once in the main build.
do_compile_ptest_base() {
}
do_install_ptest_base() {
}
