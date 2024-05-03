def mender_feature_is_enabled(feature, if_true, if_false, d):
    return if_true if feature in mender_features_list(d) else if_false

def mender_features_list(d):
    enabled = d.getVar('MENDER_FEATURES_ENABLE')
    if enabled is None:
        return ""
    else:
        enabled = enabled.split()

    disabled = d.getVar('MENDER_FEATURES_DISABLE')
    if disabled is None:
        disabled = []
    else:
        disabled = disabled.split()

    return [feature for feature in enabled if feature not in disabled]

def mender_features(d, separator=" "):
    return separator.join(mender_features_list(d))

MENDER_FEATURES = "${@mender_features(d)}"
DISTROOVERRIDES:append = ":${@mender_features(d, separator=':')}"

python() {
    # Add all possible Mender features here. This list is here to have an
    # authoritative list of all distro features that Mender provides.
    # Each one will also define the same string in DISTROOVERRIDES.
    available_features = {

        # For GRUB, use BIOS for booting, instead of the default, UEFI.
        'mender-bios',

        # Integration with GRUB.
        'mender-grub',

        # Enabled by GRUB/systemd-boot to extend UEFI overlay recipes.
        'mender-efi-boot',

        # Install of mender-auth, with the minimum components.
        'mender-auth-install',

        # Install of mender-update, with the minimum components. This includes
        # no references to specific partition layouts.
        'mender-update-install',

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

        # Use Mender together with systemd-boot.
        'mender-systemd-boot',

        # Enable Mender configuration specific to UBI.
        'mender-ubi',

        # Use Mender together with U-Boot.
        'mender-uboot',

        # Use PARTUUID to set fixed drive locations.
        'mender-partuuid',

        # Use PARTLABEL to avoid hardcoded drive device path.
        'mender-partlabel',

        # Setup the systemd machine ID to be persistent across OTA updates.
        'mender-persist-systemd-machine-id',

        # Enable dynamic resizing of the data filesystem through systemd's growfs
        'mender-growfs-data',

        # Enable the testing/* layers and functionality
        'mender-testing-enabled',

        # Enable UEFI Capsule artifact generation
        'mender-image-uefi-capsule',
    }

    # Verify that all 'mender-' features are added using MENDER_FEATURES_ENABLE
    # and MENDER_FEATURES_DISABLE variables. This is important because we base
    # some decisions on these variables, and then fill MENDER_FEATURES, which
    # would give infinite recursion if we based the decision directly on
    # MENDER_FEATURES.
    if mender_features(d) != d.getVar('MENDER_FEATURES'):
        bb.fatal("Do not assign anything to MENDER_FEATURES. Use MENDER_FEATURES_ENABLE and MENDER_FEATURES_DISABLE.")

    for feature in d.getVar('MENDER_FEATURES').split():
        if feature not in available_features:
            bb.fatal("%s from MENDER_FEATURES_ENABLE or MENDER_FEATURES is not a valid Mender feature."
                     % feature)
}

inherit ${@'' if (d.getVar('MENDER_FEATURES_ENABLE') == None) else 'mender-setup'}
