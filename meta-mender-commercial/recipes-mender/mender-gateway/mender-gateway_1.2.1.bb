require mender-gateway.inc

# DO NOT change the checksum here without make sure that ALL licenses (including
# dependencies) are included in the LICENSE variable below.
LICENSE = "Mender-Yocto-Layer-License.md & Apache-2.0 & BSD-2-Clause & BSD-3-Clause & ISC & MIT"
LICENSE_FLAGS = "commercial_mender-yocto-layer-license"
LIC_FILES_CHKSUM = " \
    file://licenses/LICENSE.md;md5=ddb0c461e9cc224aa6aff51b108f26b8 \
    file://licenses/vendor/github.com/mendersoftware/go-lib-micro/LICENSE;md5=e33ec9ac79630c915f82b11a3d4545e9 \
    file://licenses/vendor/github.com/pkg/errors/LICENSE;md5=6fe682a02df52c6653f33bd0f7126b5a \
    file://licenses/vendor/github.com/mendersoftware/filelock/LICENSE;md5=5d4950ecb7b26d2c5e4e7b4e0dd74707 \
    file://licenses/vendor/github.com/fsnotify/fsnotify/LICENSE;md5=8bae8b116e2cfd723492b02d9a212fe2 \
    file://licenses/vendor/github.com/google/uuid/LICENSE;md5=88073b6dd8ec00fe09da59e0b6dfded1 \
    file://licenses/vendor/github.com/pmezard/go-difflib/LICENSE;md5=e9a2ebb8de779a07500ddecca806145e \
    file://licenses/vendor/github.com/spf13/pflag/LICENSE;md5=1e8b7dc8b906737639131047a590f21d \
    file://licenses/vendor/golang.org/x/sync/LICENSE;md5=5d4950ecb7b26d2c5e4e7b4e0dd74707 \
    file://licenses/vendor/golang.org/x/sys/LICENSE;md5=5d4950ecb7b26d2c5e4e7b4e0dd74707 \
    file://licenses/vendor/github.com/davecgh/go-spew/LICENSE;md5=c06795ed54b2a35ebeeb543cd3a73e56 \
    file://licenses/vendor/github.com/sirupsen/logrus/LICENSE;md5=8dadfef729c08ec4e631c4f6fc5d43a0 \
    file://licenses/vendor/github.com/stretchr/objx/LICENSE;md5=d023fd31d3ca39ec61eec65a91732735 \
    file://licenses/vendor/github.com/stretchr/testify/LICENSE;md5=188f01994659f3c0d310612333d2a26f \
    file://licenses/vendor/gopkg.in/yaml.v3/LICENSE;md5=3c91c17266710e16afdbb2b6d15c761c \
"

# Enable this in Betas, and in branches that cannot carry this major version as
# default.
# Downprioritize this recipe in version selections.
# DEFAULT_PREFERENCE = "-1"
