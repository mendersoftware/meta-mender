GRUB_MENDER_GRUBENV_REV = "081c20bc7e047c6cd381e39919bdfbdd34f48849"
GRUB_MENDER_GRUBENV_SRC_URI ?= "git://github.com/mendersoftware/grub-mender-grubenv;protocol=https;branch=master;rev=${GRUB_MENDER_GRUBENV_REV}"

GRUB_BUILDIN = "boot linux ext2 fat serial part_msdos part_gpt normal \
                efi_gop iso9660 configfile search loadenv test \
                cat echo gcry_sha256 halt hashsum sleep reboot regexp \
                loadenv test xfs"
