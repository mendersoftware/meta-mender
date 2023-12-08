require mender-client-go.inc
require mender-client_git.inc

DEPENDS = "xz openssl"
RDEPENDS:${PN} = "liblzma openssl"

# 3.4 and older mender-client versions need mender-artifact-info.
RDEPENDS:${PN}:append = "${@mender_maybe_artifact_info(d)}"

PV = "${@mender_version_from_preferred_version(d)}"
