FILESEXTRAPATHS_prepend := "${THISDIR}/files:"

# This works around a somewhat tricky situation: We want to apply the patches
# below to the Linux kernel recipe. However, we don't know the name of the
# recipe upfront, because many layers use their own kernels. However, we know
# with reasonable certainty that it starts with "linux-" (the name of this
# bbappend file), and that it should be listed in
# "PREFERRED_PROVIDER_virtual/kernel". Using those two pieces of information, we
# auto-provide a patch by matching the name of the package being built with the
# PREFERRED_PROVIDER. The reason we can not simply match all packages, is that
# there are recipes that start with "linux-" which are not kernels, such as
# "linux-libc-headers".
def if_kernel_recipe(if_true, if_false, d):
    if d.getVar('PREFERRED_PROVIDER_virtual/kernel') == d.getVar('PN'):
        return if_true
    else:
        return if_false

SRC_URI_append_mender-grub_arm = "${@if_kernel_recipe(' file://enable_efi_stub.cfg', '', d)}"
SRC_URI_append_mender-grub_aarch64 = "${@if_kernel_recipe(' file://enable_efi_stub.cfg', '', d)}"
