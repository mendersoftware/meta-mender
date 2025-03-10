GRUB_MENDER_GRUBENV_REV ?= "e411fd6a9084c4372df099d1656c95399e858459"
GRUB_MENDER_GRUBENV_SRC_URI ?= "git://github.com/mendersoftware/grub-mender-grubenv;protocol=https;branch=tmp-ME-458;rev=${GRUB_MENDER_GRUBENV_REV}"

GRUB_BUILDIN = "boot linux ext2 fat serial part_msdos part_gpt normal \
                efi_gop iso9660 configfile search loadenv test \
                cat echo gcry_sha256 halt hashsum sleep reboot regexp \
                loadenv test xfs"
