require mender-client-cpp.inc
require mender-client_git.inc
require mender_5.1.x.inc

PV = "${@mender_version_from_preferred_version(d)}"
