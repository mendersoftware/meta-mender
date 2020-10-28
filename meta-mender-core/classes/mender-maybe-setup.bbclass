def mender_feature_is_enabled(feature, if_true, if_false, d):
    in_enable = bb.utils.contains('MENDER_FEATURES_ENABLE', feature, True, False, d)
    in_disable = bb.utils.contains('MENDER_FEATURES_DISABLE', feature, True, False, d)

    if in_enable and not in_disable:
        return if_true
    else:
        return if_false

# MENDER_FEATURES_ENABLE and MENDER_FEATURES_DISABLE map to
# DISTRO_FEATURES_BACKFILL and DISTRO_FEATURES_BACKFILL_CONSIDERED,
# respectively.
DISTRO_FEATURES_BACKFILL_append = " ${MENDER_FEATURES_ENABLE}"
DISTRO_FEATURES_BACKFILL_CONSIDERED_append = " ${MENDER_FEATURES_DISABLE}"

python() {
    # Add all possible Mender features here. This list is here to have an
    # authoritative list of all distro features that Mender provides.
    # Each one will also define the same string in DISTROOVERRIDES.
    mender_features = {

        # For GRUB, use BIOS for booting, instead of the default, UEFI.
        'mender-bios',

        # Integration with GRUB.
        'mender-grub',

        # Install of Mender, with the minimum components. This includes no
        # references to specific partition layouts.
        'mender-client-install',

        # Include components for Mender-partitioned images. This will create
        # files that rely on the Mender partition layout.
        'mender-image',

        # Include components for generating a BIOS GPT image.
        'mender-image-gpt',

        # Include components for generating a BIOS image.
        'mender-image-bios',

        # Include components for generating an SD image.
        'mender-image-sd',

        # Include components for generating a UBI image.
        'mender-image-ubi',

        # Include components for generating a UEFI image.
        'mender-image-uefi',

        # Include Mender as a systemd service.
        'mender-systemd',

        # Enable Mender configuration specific to UBI.
        'mender-ubi',

        # Use Mender together with U-Boot.
        'mender-uboot',

        # Use PARTUUID to set fixed drive locations.
        'mender-partuuid',

        # Setup the systemd machine ID to be persistent across OTA updates.
        'mender-persist-systemd-machine-id',

        # Enable dynamic resizing of the data filesystem through systemd's growfs
        'mender-growfs-data',

        # Enable the testing/* layers and functionality
        'mender-testing-enabled',
    }

    mfe = d.getVar('MENDER_FEATURES_ENABLE')
    mfe = mfe.split() if mfe is not None else []
    mfd = d.getVar('MENDER_FEATURES_DISABLE')
    mfd = mfd.split() if mfd is not None else []
    for feature in mfe + mfd:
        if not feature.startswith('mender-'):
            bb.fatal("%s in MENDER_FEATURES_ENABLE or MENDER_FEATURES_DISABLE is not a Mender feature."
                     % feature)

    for feature in d.getVar('DISTRO_FEATURES').split():
        if feature.startswith("mender-"):
            if feature not in mender_features:
                bb.fatal("%s from MENDER_FEATURES_ENABLE or DISTRO_FEATURES is not a valid Mender feature."
                         % feature)
            d.setVar('DISTROOVERRIDES_append', ':%s' % feature)

            # Verify that all 'mender-' features are added using MENDER_FEATURES
            # variables. This is important because we base some decisions on
            # these variables, and then fill DISTRO_FEATURES, which would give
            # infinite recursion if we based the decision directly on
            # DISTRO_FEATURES.
            if feature not in mfe or feature in mfd:
                bb.fatal(("%s is not added using MENDER_FEATURES_ENABLE and "
                          + "MENDER_FEATURES_DISABLE variables. Please make "
                          + "sure that the feature is enabled using "
                          + "MENDER_FEATURES_ENABLE, and is not in "
                          + "MENDER_FEATURES_DISABLE.")
                         % feature)
}

inherit ${@'' if (d.getVar('MENDER_FEATURES_ENABLE') == None) else 'mender-setup'}
