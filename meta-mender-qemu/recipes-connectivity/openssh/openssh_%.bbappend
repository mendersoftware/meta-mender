do_install:append_mender-systemd () {
	install -d ${D}${systemd_unitdir}/system/network.target.wants
	ln -s ../sshdgenkeys.service ${D}${systemd_unitdir}/system/network.target.wants/
}
