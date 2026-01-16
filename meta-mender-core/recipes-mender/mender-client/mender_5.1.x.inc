FILES:mender-auth += "\
    ${datadir}/dbus-1/system-services/io.mender.AuthenticationManager.service \
"

do_install:append() {
    DESTDIR='${D}' cmake_runcmake_build --target install-dbus-service-files
}