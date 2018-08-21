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

FILESEXTRAPATHS_prepend := "${THISDIR}/files:"

LICENSE = "GPL-3.0"
SRC_URI = "file://COPYING;subdir=src"

S = "${WORKDIR}/src"

LIC_FILES_CHKSUM = "file://COPYING;md5=d32239bcb673463ab874e80d47fae504"

PROVIDES = "grub-efi"
RPROVIDES_${PN} = "grub-efi"

SRC_URI_append_arm = " file://grub-efi-bootarm.efi"

COMPATIBLE_HOSTS = "arm"

inherit deploy

do_configure() {
    if [ "${KERNEL_IMAGETYPE}" = "uImage" ]; then
        bbfatal "GRUB is not compatible with KERNEL_IMAGETYPE = uImage. Please change it to either zImage or bzImage."
    fi
}

do_deploy() {
    install -m 644 ${WORKDIR}/grub-efi-bootarm.efi ${DEPLOYDIR}/
}
addtask do_deploy after do_patch

INSANE_SKIP_${PN} = "already-stripped"
