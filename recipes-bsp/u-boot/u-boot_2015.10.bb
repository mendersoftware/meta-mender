require u-boot.inc

DEPENDS += "dtc-native"

# This revision corresponds to the tag "v2015.10"
# We use the revision in order to avoid having to fetch it from the
# repo during parse
SRCREV = "5ec0003b19cbdf06ccd6941237cbc0d1c3468e2d"

PV = "v2015.10+git${SRCPV}"
