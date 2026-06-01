require mender-orchestrator.inc

LICENSE = "Mender-Yocto-Layer-License.md & Apache-2.0 & MIT & CC0-1.0 & BSL-1.0 & BSD-3-Clause"
LICENSE_FLAGS = "commercial_mender-yocto-layer-license"
LIC_FILES_CHKSUM = " \
    file://licenses/LICENSE;md5=425e73757010d92651a87c6338ebce7c \
    file://licenses/tests/integration/mender_integration/LICENSE;md5=f92624f2343d21e1986ca36f82756029 \
    file://licenses/vendor/mender/LICENSE;md5=f92624f2343d21e1986ca36f82756029 \
    file://licenses/vendor/mender/src/common/vendor/json/LICENSE.MIT;md5=3b489645de9825cca5beeb9a7e18b6eb \
    file://licenses/vendor/mender/src/common/vendor/json/docs/mkdocs/docs/home/license.md;md5=0b50ae6ab6b292c61ea813fc02dafce5 \
    file://licenses/vendor/mender/src/common/vendor/tiny-process-library/LICENSE;md5=14d72bb1dc7487cee6c51cedd497eccd \
    file://licenses/vendor/mender/src/common/vendor/yaml-cpp/LICENSE;md5=6a8aaf0595c2efc1a9c2e0913e9c1a2c \
    file://licenses/vendor/mender/src/common/vendor/expected/COPYING;md5=65d3616852dbf7b1a6d4b53b00626032 \
    file://licenses/vendor/mender/src/common/vendor/optional-lite/LICENSE.txt;md5=e4224ccaecb14d942c71d31bef20d78c \
    file://licenses/vendor/mender/src/common/vendor/yaml-cpp/test/googletest-1.13.0/LICENSE;md5=cbbd27594afd089daa160d3a16dd515a \
"

# Enable this in Betas, and in branches that cannot carry this major version as
# default.
# Downprioritize this recipe in version selections.
# DEFAULT_PREFERENCE = "-1"
