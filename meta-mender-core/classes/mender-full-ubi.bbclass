# THIS IS HIGHLY EXPERIMENTAL AND COMPLETELY UNSUPPORTED! DO NOT EXPECT MENDER
# TO WORK IF YOU INCLUDE THIS CLASS. THIS IS ONLY FOR PEOPLE THAT WANT TO HELP
# AND DEVELOP UBIFS SUPPORT IN MENDER.

# Class for those who want to enable all Mender required features for UBI based
# devices.

inherit mender-uboot
inherit mender-image
inherit mender-image-ubi
inherit mender-install
inherit mender-install-ubi
inherit mender-systemd
