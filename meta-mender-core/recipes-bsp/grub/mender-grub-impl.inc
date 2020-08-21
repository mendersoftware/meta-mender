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


python do_setcorelocation () {
}

python do_setcorelocation_mender-bios () {
    coreLoc = int(d.getVar('MENDER_IMAGE_BOOTLOADER_BOOTSECTOR_OFFSET'))
    # Location for the diskboot.img is held in boot.img as a LBA48 starting at
    # From boot.h GRUB_BOOT_MACHINE_KERNEL_SECTOR
    # If more machines are supported byte sector and byte order may need to change
    tmpInt = 0x5C
    some_bytes = coreLoc.to_bytes(6, byteorder='little')
    f = open(d.getVar('B') + "/grub-core/boot.img", "r+b")
    f.seek(tmpInt)
    f.write(some_bytes)
    f.close()

    # The rest of core.img is by default 1 sector after the disk boot.
    coreLoc = (int(d.getVar('MENDER_IMAGE_BOOTLOADER_BOOTSECTOR_OFFSET')) + 1)
    # diskboot.S defines this sector as 0x200 - GRUB_BOOT_MACHINE_LIST_SIZE(0xC)
    # If more machines are supported byte sector and byte order may need to change
    tmpInt = 0x1F4
    some_bytes = coreLoc.to_bytes(6, byteorder='little')
    f = open(d.getVar('B') + "/grub-core/diskboot.img", "r+b")
    f.seek(tmpInt)
    f.write(some_bytes)
    f.close()
}
addtask do_setcorelocation before do_mkimage after do_compile
do_setcorelocation[vardeps] = " \
    MENDER_IMAGE_BOOTLOADER_BOOTSECTOR_OFFSET \
"


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
addtask mkimage before do_deploy after do_setcorelocation


do_deploy() {
    :
}

do_deploy_mender-bios() {
    install -m 644 ${B}/grub-core.img ${DEPLOYDIR}/
    install -m 644 ${B}/grub-core/boot.img ${DEPLOYDIR}/
}
addtask do_deploy after do_setcorelocation
