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

FILESEXTRAPATHS:prepend := "${THISDIR}/files:"

LICENSE = "GPL-3.0-or-later"
LIC_FILES_CHKSUM = "file://${COREBASE}/meta/files/common-licenses/GPL-3.0-or-later;md5=1c76c4cc354acaac30ed4d5eefea7245"

URL_BASE ?= "https://downloads.mender.io/grub-mender-grubenv/grub-efi"

SRC_URI = " \
    ${GRUB_MENDER_GRUBENV_SRC_URI} \
    ${URL_BASE}/${PV}-grub-mender-grubenv-${GRUB_MENDER_GRUBENV_REV}/${HOST_ARCH}/grub-efi-${EFI_BOOT_IMAGE};md5sum=63c8f8570b763b59dd2a26f372e03155 \
    ${URL_BASE}/${PV}-grub-mender-grubenv-${GRUB_MENDER_GRUBENV_REV}/${HOST_ARCH}/grub-editenv;md5sum=2c5e943a0acc4a6bd385a9d3f72b637b \
"

S = "${WORKDIR}/git"

MENDER_EFI_LOADER ?= ""

require ${@'uboot_version_logic.inc' if d.getVar('MENDER_EFI_LOADER').startswith('u-boot') else ''}

DEPENDS:append = " ${MENDER_EFI_LOADER}"

PROVIDES = "grub-efi grub-editenv"
RPROVIDES:${PN} = "grub-efi grub-editenv"

COMPATIBLE_HOST = "arm|aarch64"

FILES:${PN} = " \
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

INSANE_SKIP:${PN} = "already-stripped"
