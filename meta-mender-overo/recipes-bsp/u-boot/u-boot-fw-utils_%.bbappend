FILESEXTRAPATHS_prepend := "${THISDIR}/files:"

SRC_URI_append_overo = " file://fw_env.config.default "

require u-boot-overo.inc
