require mender-artifact.inc

################################################################################
#-------------------------------------------------------------------------------
# THINGS TO CONSIDER FOR EACH RELEASE:
# - SRC_URI (particularly "branch")
# - SRCREV
# - DEFAULT_PREFERENCE
#-------------------------------------------------------------------------------

SRC_URI = "git://github.com/mendersoftware/mender-artifact.git;protocol=https;branch=3.10.x"

# Tag: 3.10.1
SRCREV = "48a9eb08b04fc71bf83cce626fc87a63eea25c73"

# Enable this in Betas, and in branches that cannot carry this major version as
# default.
# Downprioritize this recipe in version selections.
# DEFAULT_PREFERENCE = "-1"

################################################################################

# DO NOT change the checksum here without make sure that ALL licenses (including
# dependencies) are included in the LICENSE variable below. Note that for
# releases, we must check the LIC_FILES_CHKSUM.sha256 file, not the LICENSE
# file.
LICENSE = "Apache-2.0 & BSD-2-Clause & BSD-3-Clause & ISC & MIT"

LIC_FILES_CHKSUM = " \
    file://src/github.com/mendersoftware/mender-artifact/LICENSE;md5=b4b4cfdaea6d61aa5793b92efd42e081 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/minio/sha256-simd/LICENSE;md5=3b83ef96387f14655fc854ddc3c6bd57 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/mendersoftware/progressbar/LICENSE;md5=dcac2e5bf81a6fe99b034aaaaf1b2019 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/google.golang.org/genproto/LICENSE;md5=3b83ef96387f14655fc854ddc3c6bd57 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/google.golang.org/grpc/LICENSE;md5=3b83ef96387f14655fc854ddc3c6bd57 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/google.golang.org/appengine/LICENSE;md5=3b83ef96387f14655fc854ddc3c6bd57 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/cloud.google.com/go/kms/LICENSE;md5=3b83ef96387f14655fc854ddc3c6bd57 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/cloud.google.com/go/iam/LICENSE;md5=3b83ef96387f14655fc854ddc3c6bd57 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/cloud.google.com/go/compute/LICENSE;md5=3b83ef96387f14655fc854ddc3c6bd57 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/go.opencensus.io/LICENSE;md5=175792518e4ac015ab6696d16c4f607e \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/golang/groupcache/LICENSE;md5=19cbd64715b51267a47bf3750cc6a8a5 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/gopkg.in/square/go-jose.v2/LICENSE;md5=3b83ef96387f14655fc854ddc3c6bd57 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/oklog/run/LICENSE;md5=86d3f3a95c324c9479bd8986968f4327 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/mendersoftware/openssl/LICENSE;md5=19cbd64715b51267a47bf3750cc6a8a5 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/googleapis/enterprise-certificate-proxy/LICENSE;md5=3b83ef96387f14655fc854ddc3c6bd57 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/pkg/errors/LICENSE;md5=6fe682a02df52c6653f33bd0f7126b5a \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/pmezard/go-difflib/LICENSE;md5=e9a2ebb8de779a07500ddecca806145e \
    file://src/github.com/mendersoftware/mender-artifact/vendor/golang.org/x/sys/LICENSE;md5=5d4950ecb7b26d2c5e4e7b4e0dd74707 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/remyoudompheng/go-liblzma/LICENSE;md5=344ad0e1a666fa2b8eccea6b1b742e42 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/klauspost/compress/LICENSE;md5=d0fd9ebda39468b51ff4539c9fbb13a8 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/russross/blackfriday/v2/LICENSE.txt;md5=ecf8a8a60560c35a862a4a545f2db1b3 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/google/go-cmp/LICENSE;md5=4ac66f7dea41d8d116cb7fb28aeff2ab \
    file://src/github.com/mendersoftware/mender-artifact/vendor/golang.org/x/net/LICENSE;md5=5d4950ecb7b26d2c5e4e7b4e0dd74707 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/golang.org/x/oauth2/LICENSE;md5=5d4950ecb7b26d2c5e4e7b4e0dd74707 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/golang.org/x/text/LICENSE;md5=5d4950ecb7b26d2c5e4e7b4e0dd74707 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/golang.org/x/crypto/LICENSE;md5=5d4950ecb7b26d2c5e4e7b4e0dd74707 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/golang.org/x/time/LICENSE;md5=5d4950ecb7b26d2c5e4e7b4e0dd74707 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/google.golang.org/api/LICENSE;md5=a651bb3d8b1c412632e28823bb432b40 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/google.golang.org/api/internal/third_party/uritemplates/LICENSE;md5=4ee4feb2b545c2231749e5c54ace343e \
    file://src/github.com/mendersoftware/mender-artifact/vendor/google.golang.org/protobuf/LICENSE;md5=02d4002e9171d41a8fad93aa7faf3956 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/golang/protobuf/LICENSE;md5=939cce1ec101726fa754e698ac871622 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/googleapis/gax-go/v2/LICENSE;md5=0dd48ae8103725bd7b401261520cdfbb \
    file://src/github.com/mendersoftware/mender-artifact/vendor/golang.org/x/crypto/LICENSE;md5=5d4950ecb7b26d2c5e4e7b4e0dd74707 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/golang.org/x/time/LICENSE;md5=5d4950ecb7b26d2c5e4e7b4e0dd74707 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/golang/snappy/LICENSE;md5=b8b79c7d4cda128290b98c6a21f9aac6 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/gopkg.in/square/go-jose.v2/json/LICENSE;md5=591778525c869cdde0ab5a1bf283cd81 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/pierrec/lz4/LICENSE;md5=09ece85f3c312a63b522bfc6ebd44943 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/klauspost/compress/internal/snapref/LICENSE;md5=b8b79c7d4cda128290b98c6a21f9aac6 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/davecgh/go-spew/LICENSE;md5=c06795ed54b2a35ebeeb543cd3a73e56 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/stretchr/testify/LICENSE;md5=188f01994659f3c0d310612333d2a26f \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/urfave/cli/LICENSE;md5=75d9e324acacf92aca82397b81c225b0 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/sirupsen/logrus/LICENSE;md5=8dadfef729c08ec4e631c4f6fc5d43a0 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/klauspost/pgzip/LICENSE;md5=a6862811c790a468c5d82d68e717c154 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/cpuguy83/go-md2man/v2/LICENSE.md;md5=80794f9009df723bbc6fe19234c9f517 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/gopkg.in/yaml.v3/LICENSE;md5=3c91c17266710e16afdbb2b6d15c761c \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/mattn/go-isatty/LICENSE;md5=f509beadd5a11227c27b5d2ad6c9f2c6 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/klauspost/cpuid/v2/LICENSE;md5=00d6f962401947482d082858f7ba2ff3 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/go.uber.org/atomic/LICENSE.txt;md5=1caee86519456feda989f8a838102b50 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/mitchellh/go-homedir/LICENSE;md5=3f7765c3d4f58e1f84c4313cecf0f5bd \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/mitchellh/go-testing-interface/LICENSE;md5=96ada10a9e51c98c4656f2cede08c673 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/mitchellh/mapstructure/LICENSE;md5=3f7765c3d4f58e1f84c4313cecf0f5bd \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/mitchellh/copystructure/LICENSE;md5=56da355a12d4821cda57b8f23ec34bc4 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/mitchellh/reflectwalk/LICENSE;md5=3f7765c3d4f58e1f84c4313cecf0f5bd \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/ryanuber/go-glob/LICENSE;md5=d2c81b3028eb947731a58fb068c7dff4 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/mattn/go-colorable/LICENSE;md5=24ce168f90aec2456a73de1839037245 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/fatih/color/LICENSE.md;md5=316e6d590bdcde7993fb175662c0dd5a \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/armon/go-radix/LICENSE;md5=cb04212e101fbbd028f325e04ad45778 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/armon/go-metrics/LICENSE;md5=d2d77030c0183e3d1e66d26dc1f243be \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/cenkalti/backoff/v3/LICENSE;md5=1571d94433e3f3aa05267efd4dbea68b \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/hashicorp/go-hclog/LICENSE;md5=ec7f605b74b9ad03347d0a93a5cc7eb8 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/klauspost/compress/zstd/internal/xxhash/LICENSE.txt;md5=802da049c92a99b4387d3f3d91b00fa9 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/hashicorp/go-secure-stdlib/strutil/LICENSE;md5=65d26fcc2f35ea6a181ac777e42db1ea \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/hashicorp/go-secure-stdlib/parseutil/LICENSE;md5=65d26fcc2f35ea6a181ac777e42db1ea \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/hashicorp/errwrap/LICENSE;md5=b278a92d2c1509760384428817710378 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/hashicorp/hcl/LICENSE;md5=b278a92d2c1509760384428817710378 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/hashicorp/go-cleanhttp/LICENSE;md5=65d26fcc2f35ea6a181ac777e42db1ea \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/hashicorp/go-version/LICENSE;md5=b278a92d2c1509760384428817710378 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/hashicorp/go-rootcerts/LICENSE;md5=65d26fcc2f35ea6a181ac777e42db1ea \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/hashicorp/go-retryablehttp/LICENSE;md5=65d26fcc2f35ea6a181ac777e42db1ea \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/hashicorp/go-uuid/LICENSE;md5=65d26fcc2f35ea6a181ac777e42db1ea \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/hashicorp/go-plugin/LICENSE;md5=d44fdeb607e2d2614db9464dbedd4094 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/hashicorp/go-sockaddr/LICENSE;md5=9741c346eef56131163e13b9db1241b3 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/hashicorp/vault/sdk/LICENSE;md5=bffc21c92b5f3adcbbb06f8e0067e786 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/hashicorp/vault/api/LICENSE;md5=bffc21c92b5f3adcbbb06f8e0067e786 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/hashicorp/yamux/LICENSE;md5=2dd1a9ecf92cd5617f128808f9b85b44 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/hashicorp/go-immutable-radix/LICENSE;md5=65d26fcc2f35ea6a181ac777e42db1ea \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/hashicorp/go-multierror/LICENSE;md5=d44fdeb607e2d2614db9464dbedd4094 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/hashicorp/golang-lru/LICENSE;md5=f27a50d2e878867827842f2c60e30bfc \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/hashicorp/go-secure-stdlib/mlock/LICENSE;md5=65d26fcc2f35ea6a181ac777e42db1ea \
"

DEPENDS += "xz openssl"
RDEPENDS:${PN} = "openssl"
