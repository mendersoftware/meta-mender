DESCRIPTION = "Mender demo Update Modules Artifact generators"
LICENSE = "Apache-2.0"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/Apache-2.0;md5=89aea4e17d99a7cacdbeed46a0096b10"

RDEPENDS_${PN} = "bash"

S = "${WORKDIR}/git"

inherit allarch

BBCLASSEXTEND = "native"

def mender_autorev_if_git_version(d):
    version = d.getVar("PREFERRED_VERSION_pn-mender-client")
    if not d.getVar("EXTERNALSRC") and version is not None and "git" in version:
        return d.getVar("AUTOREV")
    else:
        return "f6ffa190892202263fdb75975059fbb201adab6a"

SRCREV = '${@mender_autorev_if_git_version(d)}'

# TODO: take into account build tags and other "-git" expressions
def mender_modules_gen_version_from_mender_version(d, srcpv):
    import re
    pref_version = d.getVar("PREFERRED_VERSION_pn-mender-client")
    if pref_version is None:
        pref_version = ""
    match = re.match(r"^[0-9]+\.[0-9]+\.", pref_version)
    if match is not None:
        return pref_version

    return "master-git%s" % srcpv

PV = "${@mender_modules_gen_version_from_mender_version(d, '${SRCPV}')}"

def mender_branch_from_mender_preferred_version(d):
    import re
    pref_version = d.getVar("PREFERRED_VERSION_pn-mender-client")
    if pref_version is None:
        pref_version = ""
    match = re.match(r"^[0-9]+\.[0-9]+\.", pref_version)
    if match is not None:
        # If the preferred version is some kind of version, use the branch name
        # for that one (1.0.x style).
        return match.group(0) + "x"
    else:
        # Else return master as branch.
        return "master"

MENDER_BRANCH = "${@mender_branch_from_mender_preferred_version(d)}"
SRC_URI = "git://github.com/mendersoftware/mender;protocol=https;branch=${MENDER_BRANCH}"

FILES_${PN} = " \
    ${bindir}/directory-artifact-gen \
    ${bindir}/single-file-artifact-gen \
    ${bindir}/docker-artifact-gen \
"

do_configure() {
    true
}

do_compile() {
    true
}

do_install() {
    oe_runmake \
        -C ${S} \
        V=1 \
        prefix=${D} \
        bindir=${bindir} \
        install-modules-gen
}