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

inherit ${@'' if (d.getVar('MENDER_FEATURES_ENABLE') == None) else 'mender-setup'}
