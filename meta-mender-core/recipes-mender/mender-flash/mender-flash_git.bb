require mender-flash.inc

# The revision listed below is not really important, it's just a way to avoid
# network probing during parsing if we are not gonna build the git version
# anyway. If git version is enabled, the AUTOREV will be chosen instead of the
# SHA.
def mender_flash_autorev_if_git_version(d):
    version = d.getVar("PREFERRED_VERSION")
    if version is None or version == "":
        version = d.getVar("PREFERRED_VERSION_%s" % d.getVar('PN'))
    if not d.getVar("EXTERNALSRC") and version is not None and "git" in version:
        return d.getVar("AUTOREV")
    else:
        return "2024ad3aa12f5905473ee8eddbe36b4e1c533a50"
SRCREV ?= '${@mender_flash_autorev_if_git_version(d)}'

def mender_flash_branch_from_preferred_version(d):
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
MENDER_FLASH_BRANCH = "${@mender_flash_branch_from_preferred_version(d)}"

def mender_flash_version_from_preferred_version(d):
    pref_version = d.getVar("PREFERRED_VERSION")
    srcpv = d.getVar("SRCPV")
    if pref_version is None:
        pref_version = d.getVar("PREFERRED_VERSION_%s" % d.getVar("PN"))
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
PV = "${@mender_flash_version_from_preferred_version(d)}"

SRC_URI = "gitsm://github.com/lluiscampos/mender-flash.git;protocol=https;branch=${MENDER_FLASH_BRANCH}"

# DO NOT change the checksum here without make sure that ALL licenses (including
# dependencies) are included in the LICENSE variable below.
def mender_flash_license(branch):
    # Only one currently. If the sub licenses change we may introduce more.
    return {
               "license": "Apache-2.0",
    }
LIC_FILES_CHKSUM = " \
    file://LICENSE;md5=b4b4cfdaea6d61aa5793b92efd42e081 \
"
LICENSE = "${@mender_flash_license(d.getVar('MENDER_FLASH_BRANCH'))['license']}"

# Disables the need for every dependency to be checked, for easier development.
_MENDER_DISABLE_STRICT_LICENSE_CHECKING = "1"

# Downprioritize this recipe in version selections.
DEFAULT_PREFERENCE = "-1"
