FILESEXTRAPATHS:prepend := "${THISDIR}/patches:"
SRC_URI:append = "${@bb.utils.contains( \
    'MENDER_FEATURES', \
    'mender-image', \
    ' file://0001-Do-not-use-metadata_csum-feature-on-ext4-by-default.patch', \
    '', \
    d \
)}"
