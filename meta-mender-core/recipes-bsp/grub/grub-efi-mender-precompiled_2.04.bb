################################################################################
# A recipe that provides precompiled binaries for ARMv5 for:
# * The grub-efi-bootarm.efi EFI bootloader
#
# The motivation for this recipe is that GRUB doesn't compile correctly under
# some ARM configurations, most notable ARMv7. However an ARMv5 binary will run
# just fine even on ARMv7, but is difficult to compile using an ARMv7 toolchain.
# Hence this recipe.
#
# If a recompile is needed to update the supplied binaries, any ARMv5 target
# should work, but a pretty straightforward way is using meta-mender's
# vexpress-qemu MACHINE type and compiling grub-efi. Then grab the resulting
# binaries from the deploy directory, and replace the precompiled binaries
# supplied alongside this recipe.
################################################################################
require conf/image-uefi.conf

FILESEXTRAPATHS_prepend := "${THISDIR}/files:"

LICENSE = "GPL-3.0"
LIC_FILES_CHKSUM = "file://${COREBASE}/meta/files/common-licenses/GPL-3.0;md5=c79ff39f19dfec6d293b95dea7b07891"

URL_BASE ?= "https://d1b0l86ne08fsf.cloudfront.net/mender-convert/grub-efi"

SRC_URI = " \
    ${URL_BASE}/${PV}/${HOST_ARCH}/grub-efi-${EFI_BOOT_IMAGE};md5sum=f14815bed7a5e54fe5bb63aef3da96bf \
    ${URL_BASE}/${PV}/${HOST_ARCH}/grub-editenv;md5sum=2c5e943a0acc4a6bd385a9d3f72b637b \
"

S = "${WORKDIR}/src"

include version_logic.inc

PROVIDES = "grub-efi grub-editenv"
RPROVIDES_${PN} = "grub-efi grub-editenv"

COMPATIBLE_HOST = "arm|aarch64"

FILES_${PN} = " \
    ${EFI_FILES_PATH}/${EFI_BOOT_IMAGE} \
    ${bindir}/grub-editenv \
"

do_configure() {
    if [ "${KERNEL_IMAGETYPE}" = "uImage" ]; then
        bbfatal "GRUB is not compatible with KERNEL_IMAGETYPE = uImage. Please change it to either zImage or bzImage."
    fi
}

do_install() {
    install -d -m 755 ${D}${EFI_FILES_PATH}
    install -m 644 ${WORKDIR}/grub-efi-${EFI_BOOT_IMAGE} ${D}${EFI_FILES_PATH}/${EFI_BOOT_IMAGE}

    install -d -m 755 ${D}${bindir}
    install -m 755 ${WORKDIR}/grub-editenv ${D}${bindir}/
}

INSANE_SKIP_${PN} = "already-stripped"
