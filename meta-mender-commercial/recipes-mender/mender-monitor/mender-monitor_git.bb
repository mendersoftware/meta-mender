require mender-monitor.inc

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
        if len(filenames) != 1:
            bb.error("Expected exactly one file, found: %s" % filenames)
        filename = filenames[0]
        # Now extract the git sha from the filename
        m = re.match(r".*/mender-monitor-([0-9a-f]+)\.tar\.gz", filename)
        if m is None:
            # No match probably means that the tarball is a tagged version, in
            # which case this recipe is not to be used but still needs to parse
            return ""
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
        # Else return "master-git${SRCREV}".
        return "master-git%s" % srcrev

PV = "${@mender_monitor_version_from_preferred_version(d, '${SRCREV}')}"

# Skip version check
MENDER_DEVMODE = "true"

# Downprioritize this recipe in version selections.
DEFAULT_PREFERENCE = "-1"
