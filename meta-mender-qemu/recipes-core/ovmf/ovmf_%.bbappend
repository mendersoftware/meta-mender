FILESEXTRAPATHS:prepend := "${THISDIR}/patches:"

# edk2-stable202511 takes leftover RAM at 0x812000 for an IGVM memory map, so a
# warm reboot can end in a silent triple fault loop. Fixed in edk2-stable202602.
SRC_URI:append = " file://0001-OvmfPkg-PlatformInitLib-reserve-igvm-parameter-area.patch"
