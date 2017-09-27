FILESEXTRAPATHS_prepend := "${THISDIR}/files:"

SRC_URI_append_colibri-imx7 = " \
    file://0001-colibri-imx7-Mender-QA-extend-env-to-support-integra.patch \
    file://0002-colibri-imx7-Mender-QA-reset-the-board-on-panic.patch \
    "
