inherit image-buildinfo

DEVICE_TYPE ?= "${MACHINE}"
IMAGE_ID = "${PN}-${DATETIME}"
IMAGE_BUILDINFO_VARS = "DISTRO DATETIME PN IMAGE_ID DEVICE_TYPE"

buildinfo_mender () {
cat > ${IMAGE_ROOTFS}${sysconfdir}/build_mender << END
------------------------
Mender device manifest:|
------------------------
${@buildinfo_target(d)}
------------------------
END
}

IMAGE_PREPROCESS_COMMAND += "buildinfo_mender;"
