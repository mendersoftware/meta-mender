GRUB_MENDER_GRUBENV_REV = "f39c2c7ec7c9c24aae0108a9b04a0e6e61a3e96b"
GRUB_MENDER_GRUBENV_SRC_URI ?= "git://github.com/mendersoftware/grub-mender-grubenv;protocol=https;branch=master;rev=${GRUB_MENDER_GRUBENV_REV}"

GRUB_BUILDIN = "boot linux ext2 fat serial part_msdos part_gpt normal \
                efi_gop iso9660 configfile search loadenv test \
                cat echo gcry_sha256 halt hashsum sleep reboot regexp \
                loadenv test"
