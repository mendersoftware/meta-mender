################################################################################
# A recipe that provides precompiled binaries for ARMv5 for:
# * The grub-efi-bootarm.efi EFI bootloader
#
# The motivation for this recipe is that GRUB doesn't compile correctly under
# some ARM configurations, most notable ARMv7. However an ARMv5 binary will run
# just fine even on ARMv7, but is difficult to compile using an ARMv7 toolchain.
# Hence this recipe.
#
# The actual binaries are maintained in the grub-mender-grubenv repository, so
# look there for ways to rebuild them.
################################################################################
require conf/image-uefi.conf
inherit grub-mender-grubenv

FILESEXTRAPATHS_prepend := "${THISDIR}/files:"

LICENSE = "GPL-3.0"
LIC_FILES_CHKSUM = "file://${COREBASE}/meta/files/common-licenses/GPL-3.0;md5=c79ff39f19dfec6d293b95dea7b07891"

URL_BASE ?= "https://d1b0l86ne08fsf.cloudfront.net/grub-mender-grubenv/grub-efi"

SRC_URI = " \
    ${GRUB_MENDER_GRUBENV_SRC_URI} \
    ${URL_BASE}/${PV}-grub-mender-grubenv-${GRUB_MENDER_GRUBENV_REV}/${HOST_ARCH}/grub-efi-${EFI_BOOT_IMAGE};md5sum=7ec4b336f333f45abec86f6193326226 \
    ${URL_BASE}/${PV}-grub-mender-grubenv-${GRUB_MENDER_GRUBENV_REV}/${HOST_ARCH}/grub-editenv;md5sum=2c5e943a0acc4a6bd385a9d3f72b637b \
"

S = "${WORKDIR}/git"

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

    # Check that the prebuilt binaries have the same set of modules as the ones
    # set in the Bitbake environment.
    . ${S}/grub-efi/grub.inc
    for module in $GRUB_MODULES; do
        echo $module
    done | sort > ${WORKDIR}/grub-mender-grubenv-modules.txt
    for module in ${GRUB_BUILDIN}; do
        echo $module
    done | sort > ${WORKDIR}/bitbake-modules.txt
    if ! diff -u ${WORKDIR}/grub-mender-grubenv-modules.txt ${WORKDIR}/bitbake-modules.txt; then
        bbfatal "The list of GRUB modules is not the same in the prebuilt binaries as in the Bitbake environment. Either correct the Bitbake environment or update the prebuilt binaries."
    fi
}

do_compile() {
    # No-op, so just override the poky "smart" version.
    :
}

do_install() {
    install -d -m 755 ${D}${EFI_FILES_PATH}
    install -m 644 ${WORKDIR}/grub-efi-${EFI_BOOT_IMAGE} ${D}${EFI_FILES_PATH}/${EFI_BOOT_IMAGE}

    install -d -m 755 ${D}${bindir}
    install -m 755 ${WORKDIR}/grub-editenv ${D}${bindir}/
}

INSANE_SKIP_${PN} = "already-stripped"
