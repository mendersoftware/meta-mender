require mender-orchestrator.inc

LICENSE = "Mender-Yocto-Layer-License.md & Apache-2.0 & MIT & CC0-1.0 & BSL-1.0 & BSD-3-Clause"
LICENSE_FLAGS = "commercial_mender-yocto-layer-license"
LIC_FILES_CHKSUM = " \
    file://licenses/LICENSE;md5=bf62066192c8cf34a26d34c62f510fc5 \
    file://licenses/tests/integration/mender_integration/LICENSE;md5=f92624f2343d21e1986ca36f82756029 \
    file://licenses/tests/integration/mender-orchestrator-support/LICENSE;md5=ed7b7edaf4c941c8d3d64890db92ad92 \
    file://licenses/vendor/mender/LICENSE;md5=f92624f2343d21e1986ca36f82756029 \
    file://licenses/vendor/mender/src/common/vendor/yaml-cpp/test/gtest-1.11.0/googlemock/scripts/generator/LICENSE;md5=2c0b90db7465231447cf2dd2e8163333 \
    file://licenses/vendor/mender/src/common/vendor/json/LICENSE.MIT;md5=67f35caa1c9c8d3d990356bfecf802fb \
    file://licenses/vendor/mender/src/common/vendor/json/docs/mkdocs/docs/home/license.md;md5=a30fca2d241ce1bc9c268fc2bb7cca74 \
    file://licenses/vendor/mender/src/common/vendor/tiny-process-library/LICENSE;md5=14d72bb1dc7487cee6c51cedd497eccd \
    file://licenses/vendor/mender/src/common/vendor/yaml-cpp/LICENSE;md5=6a8aaf0595c2efc1a9c2e0913e9c1a2c \
    file://licenses/vendor/mender/src/common/vendor/expected/COPYING;md5=65d3616852dbf7b1a6d4b53b00626032 \
    file://licenses/vendor/mender/src/common/vendor/optional-lite/LICENSE.txt;md5=e4224ccaecb14d942c71d31bef20d78c \
    file://licenses/vendor/mender/src/common/vendor/yaml-cpp/test/gtest-1.11.0/LICENSE;md5=cbbd27594afd089daa160d3a16dd515a \
"

# Enable this in Betas, and in branches that cannot carry this major version as
# default.
# Downprioritize this recipe in version selections.
# DEFAULT_PREFERENCE = "-1"
