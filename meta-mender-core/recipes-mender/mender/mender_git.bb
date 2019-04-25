require mender.inc
require mender-old-makefile.inc

# The revision listed below is not really important, it's just a way to avoid
# network probing during parsing if we are not gonna build the git version
# anyway. If git version is enabled, the AUTOREV will be chosen instead of the
# SHA.
def mender_autorev_if_git_version(d):
    version = d.getVar("PREFERRED_VERSION")
    if version is None or version == "":
        version = d.getVar("PREFERRED_VERSION_%s" % d.getVar('PN'))
    if version is not None and "git" in version:
        return d.getVar("AUTOREV")
    else:
        return "f6ffa190892202263fdb75975059fbb201adab6a"
SRCREV ?= '${@mender_autorev_if_git_version(d)}'

def mender_branch_from_preferred_version(d):
    import re
    version = d.getVar("PREFERRED_VERSION")
    if version is None or version == "":
        version = d.getVar("PREFERRED_VERSION_%s" % d.getVar('PN'))
    if version is None:
        version = ""
    match = re.match(r"^[0-9]+\.[0-9]+\.", version)
    if match is not None:
        # If the preferred version is some kind of version, use the branch name
        # for that one (1.0.x style).
        return match.group(0) + "x"
    else:
        # Else return master as branch.
        return "master"
MENDER_BRANCH = "${@mender_branch_from_preferred_version(d)}"

def mender_version_from_preferred_version(d, srcpv):
    pref_version = d.getVar("PREFERRED_VERSION")
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
        # Else return the default "master-git".
        return "master-git%s" % srcpv
PV = "${@mender_version_from_preferred_version(d, '${SRCPV}')}"

SRC_URI = "git://github.com/mendersoftware/mender;protocol=https;branch=${MENDER_BRANCH}"

# DO NOT change the checksum here without make sure that ALL licenses (including
# dependencies) are included in the LICENSE variable below.
def mender_license(branch):
    if branch == "1.2.x":
        return {
                   "md5": "13741fb0210ea8a11a3e8e0247c9429c",
                   "license": "Apache-2.0 & BSD-2-Clause & BSD-3-Clause & ISC & MIT & OLDAP-2.8",
        }
    elif branch == "1.7.x":
        return {
                   "md5": "5632b9f17043c6f5f532501778595c78",
                   "license": "Apache-2.0 & BSD-2-Clause & BSD-3-Clause & ISC & MIT & OLDAP-2.8",
        }
    else:
        return {
                   "md5": "08bde78aa3411d357cefdcc4799f026b",
                   "license": "Apache-2.0 & BSD-2-Clause & BSD-3-Clause & ISC & MIT & OLDAP-2.8",
        }
LIC_FILES_CHKSUM = "file://src/github.com/mendersoftware/mender/LIC_FILES_CHKSUM.sha256;md5=${@mender_license(d.getVar('MENDER_BRANCH'))['md5']}"
LICENSE = "${@mender_license(d.getVar('MENDER_BRANCH'))['license']}"

# Downprioritize this recipe in version selections.
DEFAULT_PREFERENCE = "-1"

do_compile_ptest_base() {
   # Yocto branches sumo and older fail in Mender version 2.0
   # ptest since it uses some golang features that are only
   # available in newer branches of OE
   true
}
