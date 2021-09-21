require mender-monitor.inc

# This is the developent recipe for which the recipe version gets defined from the downloaded archive name.

def mender_monitor_srcrev_from_src_uri(d, src_uri):
    pref_version = d.getVar("PREFERRED_VERSION")
    if pref_version is not None and pref_version.find("-build") >= 0:
        # If "-build" is in the version, SRCREV won't be used for defining PV
        return ""
    else:
        # Extract SRCREV from the tarball filename
        import glob
        import re
        # Remove "file://" prefix
        src_uri_list = src_uri.split()
        if len(src_uri_list) == 0:
            # No source specified. We won't be building this component.
            return ""
        src_uri_glob = src_uri_list[0][len("file://"):]
        # Get the filename
        filenames = glob.glob(src_uri_glob)
        if len(filenames) == 0:
            bb.error("Failed to find mender monitor on path %s" % src_uri_glob)
            bb.error("Please make sure SRC_URI_pn-mender-monitor is pointing to the downloaded tarball ")
        elif len(filenames) != 1:
            bb.warning("Expected exactly one file, found: %s" % filenames)
        filename = os.path.basename(filenames[0])
        # Now extract the SRCREV from the filename
        m = re.match(r"mender-monitor-(.*)\.tar\.gz", filename)
        if m is None:
            bb.error("Cannot extract SRCREV from filename: %s" % filename)
        return m.group(1)

SRCREV = "${@mender_monitor_srcrev_from_src_uri(d, '${SRC_URI}')}"

def mender_monitor_version_from_preferred_version(d, srcrev):
    pref_version = d.getVar("PREFERRED_VERSION")
    if pref_version is not None and pref_version.find("-build") >= 0:
        # If "-build" is in the version, use the version as is. This means that
        # we can build tags with "-build" in them from this recipe, but not
        # final tags, which will need their own recipe.
        return pref_version
    else:
        return "%s" % srcrev

PV = "${@mender_monitor_version_from_preferred_version(d, '${SRCREV}')}"

# Skip version check
MENDER_DEVMODE = "true"

# Downprioritize this recipe in version selections.
DEFAULT_PREFERENCE = "-1"
