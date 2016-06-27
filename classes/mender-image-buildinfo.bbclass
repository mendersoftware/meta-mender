DEVICE_TYPE ?= "${MACHINE}"
IMAGE_ID = "${PN}-${DATETIME}"

buildinfo_mender () {
mkdir -p ${IMAGE_ROOTFS}${sysconfdir}/mender
cat > ${IMAGE_ROOTFS}${sysconfdir}/mender/build_mender << END
------------------------
Mender device manifest:|
------------------------
DEVICE_TYPE=${DEVICE_TYPE}
IMAGE_ID=${IMAGE_ID}
------------------------
END
}

IMAGE_PREPROCESS_COMMAND += "buildinfo_mender;"
