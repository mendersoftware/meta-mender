
def mender_closed_source_srcrev_from_src_uri(d, src_uri, repo_name):
    pref_version = d.getVar("PREFERRED_VERSION")
    if pref_version is None or pref_version == "":
        pref_version = d.getVar("PREFERRED_VERSION:%s" % d.getVar('PN'))
    if pref_version and pref_version.find("-build") >= 0:
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
            bb.error("Failed to find %s in path %s" % (src_uri_glob, repo_name))
            bb.error("Please make sure SRC_URI_pn-%s is pointing to the downloaded tarball " % repo_name)
        elif len(filenames) != 1:
            bb.error("Expected exactly one file, found: %s" % filenames)
        filename = os.path.basename(filenames[0])
        # Now extract the version from the filename
        m = re.match(repo_name + r"-(?:master|main)\.tar\.(?:xz|gz)", filename)
        if m:
            # Building from external tarball, do not append git info
            return ""
        m = re.match(repo_name + r"-([0-9]+\.[0-9]+\.[0-9]+(?:-build[0-9]+)?)\.tar\.(?:xz|gz)", filename)
        if m:
            # The tarball is a tagged version, in which case SRCREV is not to
            # be used but still needs to parse
            return ""
        m = re.match(repo_name + r"-([0-9a-f]{7,})\.tar\.(?:xz|gz)", filename)
        if m:
            # Building from internal tarball, append git info
            return "-git+" + m.group(1)
        # At this point the version is unknown.
        bb.fatal("Unknown version. Failed to parse %s" % filename)

def mender_closed_source_pv_from_preferred_version(d, srcrev):
    pref_version = d.getVar("PREFERRED_VERSION")
    if pref_version is None or pref_version == "":
        pref_version = d.getVar("PREFERRED_VERSION:%s" % d.getVar('PN'))
    if pref_version is not None and pref_version.find("-build") >= 0:
        # If "-build" is in the version, use the version as is. This means that
        # we can build tags with "-build" in them from this recipe, but not
        # final tags, which will need their own recipe.
        return pref_version
    # Derive branch prefix from PREFERRED_VERSION (e.g. "<branch>-git%"); fall
    # back to "master" when nothing usable is set.
    branch = "master"
    if pref_version is not None and pref_version.endswith(("-git", "-git%")):
        branch = pref_version.rsplit("-git", 1)[0]
    return "%s%s" % (branch, srcrev)

def mender_closed_source_tarball_dir_from_pv(d, pv):
    # PV is "<branch>-git+<sha>" for git builds, "<branch>" for branch
    # tarballs, or a tagged version like "1.2.3" / "1.2.3-build1". The
    # directory inside the tarball is the trailing "<sha>" for git builds,
    # otherwise the literal PV.
    if "-git+" in pv:
        return pv.split("-git+", 1)[1]
    return pv
