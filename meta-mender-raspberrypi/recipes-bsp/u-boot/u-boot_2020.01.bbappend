FILESEXTRAPATHS_prepend := "${THISDIR}/${PN}-${PV}:"

# fix cm3 u-boot booting (see: https://github.com/agherzan/meta-raspberrypi/pull/660)
SRC_URI_append_raspberrypi-cm3 = " file://0001-dm-core-Move-ofdata_to_platdata-call-earlier.patch"
