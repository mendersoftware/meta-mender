require mender-client-version-inventory-script.inc

# Special handling from Git recipe to set the release to build: for build
# candidates, take the base version as the release target, while for master
# builds, set to blank so that Makefile itself decides which json to use.
def build_release_from_preferred_version(d):
    pref_version = d.getVar("PREFERRED_VERSION")
    if pref_version is None:
        pref_version = d.getVar("PREFERRED_VERSION_%s" % d.getVar("PN"))
    if pref_version is not None and pref_version.find("-build") >= 0:
        # If "-build" is in the version, use the version as final
        return pref_version.split('-build')[0]
    else:
        # main or release branches, keep blank for the Makefile to chose the latest
        return ""
BUILD_RELEASE = "${@build_release_from_preferred_version(d)}"

# Special handling for RCONFLICTS: skip for master builds
python do_set_rconflicts () {
    if build_release_from_preferred_version(d) != "":
        actual_do_set_rconflicts(d)
    else:
        bb.warn("Skipping run_make_conflicts")
}

# The revision listed below is not really important, it's just a way to avoid
# network probing during parsing if we are not gonna build the git version
# anyway. If git version is enabled, the AUTOREV will be chosen instead of the
# SHA.
def autorev_if_git_version(d):
    version = d.getVar("PREFERRED_VERSION")
    if version is None or version == "":
        version = d.getVar("PREFERRED_VERSION:%s" % d.getVar('PN'))
    if not d.getVar("EXTERNALSRC") and version is not None and "git" in version:
        return d.getVar("AUTOREV")
    else:
        return "71c96666be221baa084b170bc892d408582a3f4d"
SRCREV ?= '${@autorev_if_git_version(d)}'

def branch_from_preferred_version(d):
    import re
    version = d.getVar("PREFERRED_VERSION")
    if version is None or version == "":
        version = d.getVar("PREFERRED_VERSION:%s" % d.getVar('PN'))
    if version is None:
        version = ""
    match = re.match(r"^[0-9]+\.[0-9]+\.", version)
    if match is not None:
        # If the preferred version is some kind of version, use the branch name
        # for that one (1.0.x style).
        return match.group(0) + "x"
    else:
        # Else return main as branch.
        return "main"
GIT_BRANCH = "${@branch_from_preferred_version(d)}"

def version_from_preferred_version(d):
    pref_version = d.getVar("PREFERRED_VERSION")
    srcpv = d.getVar("SRCPV")
    if pref_version is None:
        pref_version = d.getVar("PREFERRED_VERSION:%s" % d.getVar("PN"))
    if pref_version is not None and pref_version.find("-git") >= 0:
        # If "-git" is in the version, remove it along with any suffix it has,
        # and then readd it with commit SHA.
        return "%s-git%s" % (pref_version[0:pref_version.index("-git")], srcpv)
    elif pref_version is not None and pref_version.find("-build") >= 0:
        # If "-build" is in the version, use the version as is. This means that
        # we can build tags with "-build" in them from this recipe, but not
        # final tags, which will need their own recipe.
        return pref_version
    else:
        # Else return the default "main-git".
        return "main-git%s" % srcpv
PV = "${@version_from_preferred_version(d)}"

SRC_URI = "git://github.com/mendersoftware/mender-client-subcomponents.git;protocol=https;branch=${GIT_BRANCH}"

# DO NOT change the checksum here without make sure that ALL licenses (including
# dependencies) are included in the LICENSE variable below.
def license(branch):
    # Only one currently. If the sub licenses change we may introduce more.
    return {
               "license": "Apache-2.0",
    }
LIC_FILES_CHKSUM = " \
    file://LICENSE;md5=f92624f2343d21e1986ca36f82756029 \
"
LICENSE = "${@license(d.getVar('GIT_BRANCH'))['license']}"

# Disables the need for every dependency to be checked, for easier development.
_MENDER_DISABLE_STRICT_LICENSE_CHECKING = "1"

# Downprioritize this recipe in version selections.
DEFAULT_PREFERENCE = "-1"
