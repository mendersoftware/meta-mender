
PACKAGECONFIG_append = "${@bb.utils.contains('MENDER_FEATURES', 'mender-client-install', ' p11-kit', '', d)}"

