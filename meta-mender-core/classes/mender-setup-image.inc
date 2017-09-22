IMAGE_FSTYPES_append = "${@bb.utils.contains('DISTRO_FEATURES', 'mender-image', ' mender', '', d)}"
IMAGE_FSTYPES_append = "${@bb.utils.contains('DISTRO_FEATURES', 'mender-image-sd', ' sdimg', '', d)}"
IMAGE_FSTYPES_append = "${@bb.utils.contains('DISTRO_FEATURES', 'mender-image-ubi', ' ubimg', '', d)}"

python() {
    depends_on_mender_image = ['mender-image-sd', 'mender-image-ubi']

    features = d.getVar('DISTRO_FEATURES').split()
    for dep in depends_on_mender_image:
        if dep in features and 'mender-image' not in features:
            bb.fatal("If enabling %s in MENDER_FEATURES_ENABLE or DISTRO_FEATURES, mender-image must also be enabled"
                     % dep)
}
