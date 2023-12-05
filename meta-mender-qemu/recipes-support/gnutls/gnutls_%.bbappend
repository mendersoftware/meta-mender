
PACKAGECONFIG:class-target:append = "${@bb.utils.contains('MENDER_FEATURES', 'mender-auth-install', ' p11-kit', '', d)}"

