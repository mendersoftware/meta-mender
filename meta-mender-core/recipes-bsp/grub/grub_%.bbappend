FILESEXTRAPATHS_prepend := "${THISDIR}/files:"

include grub-mender.inc

inherit deploy

SRC_URI_append_mender-bios = " file://bios-cfg"

GRUB_TARGET_x86 = "i386-pc"
GRUB_TARGET_x86-64 = "i386-pc"

# Taken from poky's grub-efi, and removed efi part.
GRUB_BUILDIN ?= "boot linux ext2 fat serial part_msdos part_gpt normal \
                 iso9660 configfile search loadenv test"

GRUB_BUILDIN_append_mender-bios = " biosdisk"

# Needed to use grub-mkimage
DEPENDS_append = " grub-efi-native"

# No non-EFI GRUB unless we are on BIOS.
do_mkimage() {
    :
}

do_mkimage_mender-bios() {
    set -x

    cd ${B}

    # Search for the grub.cfg on the local boot media by using the built in cfg
    # file provided via this recipe
    EMBEDDED_CFG=
    if [ -e ${WORKDIR}/bios-cfg ]; then
        EMBEDDED_CFG="-c ${WORKDIR}/bios-cfg"
    fi

    grub-mkimage $EMBEDDED_CFG -p / -d ./grub-core/ \
        -O ${GRUB_TARGET} -o ./grub-core.img \
        ${GRUB_BUILDIN}
}
addtask mkimage before do_deploy after do_compile

do_deploy() {
    :
}

do_deploy_mender-bios() {
    install -m 644 ${B}/grub-core.img ${DEPLOYDIR}/
    install -m 644 ${B}/grub-core/boot.img ${DEPLOYDIR}/

    if ( ${@bb.utils.contains('IMAGE_FSTYPES', 'sdimg', 'true', 'false', d)} \
            || ${@bb.utils.contains('IMAGE_FSTYPES', 'biosimg', 'true', 'false', d)} ) \
            && [ ${MENDER_IMAGE_BOOTLOADER_BOOTSECTOR_OFFSET} != 1 ]; then
        bbwarn "The Mender GRUB setup isn't prepared to handle GRUB being flashed to any other sector than sector 1 (counting from 0). Board may not boot. Check MENDER_IMAGE_BOOTLOADER_BOOTSECTOR_OFFSET variable or flash GRUB manually by booting the board through other means and running grub-install."
    fi
}
addtask do_deploy after do_compile
