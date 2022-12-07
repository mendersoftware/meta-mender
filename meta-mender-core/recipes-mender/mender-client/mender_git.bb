require mender-client-cpp.inc
require mender-client_git.inc

LICENSE = "Apache-2.0 & BSD-3-Clause"

LIC_FILES_CHKSUM = " \
    file://LICENSE;md5=4cd0c347af5bce5ccf3b3d5439a2ea87 \
    file://vendor/json/LICENSE.MIT;md5=f969127d7b7ed0a8a63c2bbeae002588 \
    file://vendor/json/docs/mkdocs/docs/home/license.md;md5=970ea048f6ea7d04eeb3ba3ef9ebca40 \
    file://vendor/lmdbxx/UNLICENSE;md5=7246f848faa4e9c9fc0ea91122d6e680 \
"

PV = "${@mender_version_from_preferred_version(d)}"
