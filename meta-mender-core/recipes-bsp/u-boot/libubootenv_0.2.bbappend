FILESEXTRAPATHS_prepend := "${THISDIR}/patches-libubootenv:"

SRC_URI_append_mender-uboot = " \
    file://0001-Restore-ability-to-feed-script-file-via-stdin-using-.patch \
    file://0002-ubi-write-fix-invalid-envsize-ptr-to-UBI_IOCVOLUP.patch \
"
