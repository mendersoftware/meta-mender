FILESEXTRAPATHS_prepend := "${THISDIR}/files:"

SRC_URI_append_colibri-imx7 = " \
    file://0002-colibri-imx7-Mender-QA-reset-the-board-on-panic.patch \
    "
