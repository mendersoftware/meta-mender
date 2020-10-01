
PACKAGECONFIG_append = "${@bb.utils.contains('DISTRO_FEATURES', 'mender-client-install', ' p11-kit', '', d)}"

