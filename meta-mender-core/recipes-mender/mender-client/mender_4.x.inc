
# The docker module depends on bash, and of course on docker. However, docker is
# a very large requirement, which we will not mandate. Bash however, we require,
# because otherwise the Yocto QA checks will complain.
RDEPENDS:mender-update:append = "${@bb.utils.contains('PACKAGECONFIG', 'modules', ' bash', '', d)}"
