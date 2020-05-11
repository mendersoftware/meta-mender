GRUB_MENDER_GRUBENV_REV = "aa7e8f8c76c6aca6dca1820aaa42dc2cbf9762a1"
GRUB_MENDER_GRUBENV_SRC_URI ?= "git://github.com/mendersoftware/grub-mender-grubenv;protocol=https;branch=master;rev=${GRUB_MENDER_GRUBENV_REV}"

GRUB_BUILDIN = "boot linux ext2 fat serial part_msdos part_gpt normal \
                efi_gop iso9660 configfile search loadenv test \
                cat echo gcry_sha256 halt hashsum sleep reboot regexp \
                loadenv test"
