GRUB_MENDER_GRUBENV_REV ?= "eeb7ebd9e6558cf6bbe661b4f2e4e45d52efa305"
GRUB_MENDER_GRUBENV_SRC_URI ?= "git://github.com/mendersoftware/grub-mender-grubenv;protocol=https;branch=master;rev=${GRUB_MENDER_GRUBENV_REV}"

GRUB_BUILDIN = "boot linux ext2 fat serial part_msdos part_gpt normal \
                efi_gop iso9660 configfile search loadenv test \
                cat echo gcry_sha256 halt hashsum sleep reboot regexp \
                loadenv test xfs"
