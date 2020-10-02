
do_install_append () {
	# see MEN-3730, this is to align with the current default settings on raspbian
	cat >> "${D}${sysconfdir}/ssl/openssl.cnf" <<EOF
[system_default_sect]
MinProtocol = TLSv1.2
CipherString = DEFAULT@SECLEVEL=2
EOF
}
