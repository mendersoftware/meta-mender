require mender-artifact.inc

################################################################################
#-------------------------------------------------------------------------------
# THINGS TO CONSIDER FOR EACH RELEASE:
# - SRC_URI (particularly "branch")
# - SRCREV
# - DEFAULT_PREFERENCE
#-------------------------------------------------------------------------------

SRC_URI = "git://github.com/mendersoftware/mender-artifact.git;protocol=https;branch=master"

# Tag: 4.1.1
SRCREV = "aad6c379ed5e4560a530ac6a21f16351cabcf61c"

# Enable this in Betas, and in branches that cannot carry this major version as
# default.
# Downprioritize this recipe in version selections.
DEFAULT_PREFERENCE = "-1"

################################################################################

# DO NOT change the checksum here without make sure that ALL licenses (including
# dependencies) are included in the LICENSE variable below. Note that for
# releases, we must check the LIC_FILES_CHKSUM.sha256 file, not the LICENSE
# file.
LICENSE = "Apache-2.0 & BSD-2-Clause & BSD-3-Clause & ISC & MIT"

LIC_FILES_CHKSUM = " \
    file://src/github.com/mendersoftware/mender-artifact/LICENSE;md5=f92624f2343d21e1986ca36f82756029 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/minio/sha256-simd/LICENSE;md5=3b83ef96387f14655fc854ddc3c6bd57 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/mendersoftware/progressbar/LICENSE;md5=f4a60996eb58eca8e4aede01250758e6 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/google.golang.org/genproto/LICENSE;md5=3b83ef96387f14655fc854ddc3c6bd57 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/google.golang.org/genproto/googleapis/api/LICENSE;md5=3b83ef96387f14655fc854ddc3c6bd57 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/google.golang.org/genproto/googleapis/rpc/LICENSE;md5=3b83ef96387f14655fc854ddc3c6bd57 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/google.golang.org/grpc/LICENSE;md5=3b83ef96387f14655fc854ddc3c6bd57 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/cloud.google.com/go/kms/LICENSE;md5=3b83ef96387f14655fc854ddc3c6bd57 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/cloud.google.com/go/iam/LICENSE;md5=3b83ef96387f14655fc854ddc3c6bd57 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/cloud.google.com/go/compute/metadata/LICENSE;md5=3b83ef96387f14655fc854ddc3c6bd57 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/cloud.google.com/go/auth/LICENSE;md5=3b83ef96387f14655fc854ddc3c6bd57 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/cloud.google.com/go/auth/oauth2adapt/LICENSE;md5=3b83ef96387f14655fc854ddc3c6bd57 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/mendersoftware/openssl/LICENSE;md5=19cbd64715b51267a47bf3750cc6a8a5 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/googleapis/enterprise-certificate-proxy/LICENSE;md5=3b83ef96387f14655fc854ddc3c6bd57 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/go-jose/go-jose/v3/json/LICENSE;md5=591778525c869cdde0ab5a1bf283cd81 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/go-jose/go-jose/v3/LICENSE;md5=3b83ef96387f14655fc854ddc3c6bd57 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/google/s2a-go/LICENSE.md;md5=3b83ef96387f14655fc854ddc3c6bd57 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/Keyfactor/signserver-go-client-sdk/LICENSE;md5=86d3f3a95c324c9479bd8986968f4327 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/kylelemons/godebug/LICENSE;md5=3b83ef96387f14655fc854ddc3c6bd57 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/go.opentelemetry.io/otel/trace/LICENSE;md5=86d3f3a95c324c9479bd8986968f4327 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/go.opentelemetry.io/otel/LICENSE;md5=86d3f3a95c324c9479bd8986968f4327 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/go.opentelemetry.io/otel/metric/LICENSE;md5=86d3f3a95c324c9479bd8986968f4327 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/go.opentelemetry.io/contrib/instrumentation/net/http/otelhttp/LICENSE;md5=86d3f3a95c324c9479bd8986968f4327 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/go.opentelemetry.io/contrib/instrumentation/google.golang.org/grpc/otelgrpc/LICENSE;md5=86d3f3a95c324c9479bd8986968f4327 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/go.opentelemetry.io/auto/sdk/LICENSE;md5=86d3f3a95c324c9479bd8986968f4327 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/go-logr/logr/LICENSE;md5=e3fc50a88d0a364313df4b21ef20c29e \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/go-logr/stdr/LICENSE;md5=86d3f3a95c324c9479bd8986968f4327 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/pkg/errors/LICENSE;md5=6fe682a02df52c6653f33bd0f7126b5a \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/pkg/browser/LICENSE;md5=2c6b03e6a9b13bd75b50a8dbeed074da \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/pmezard/go-difflib/LICENSE;md5=e9a2ebb8de779a07500ddecca806145e \
    file://src/github.com/mendersoftware/mender-artifact/vendor/golang.org/x/sys/LICENSE;md5=7998cb338f82d15c0eff93b7004d272a \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/klauspost/compress/LICENSE;md5=d0fd9ebda39468b51ff4539c9fbb13a8 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/russross/blackfriday/v2/LICENSE.txt;md5=ecf8a8a60560c35a862a4a545f2db1b3 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/golang.org/x/net/LICENSE;md5=7998cb338f82d15c0eff93b7004d272a \
    file://src/github.com/mendersoftware/mender-artifact/vendor/golang.org/x/oauth2/LICENSE;md5=7998cb338f82d15c0eff93b7004d272a \
    file://src/github.com/mendersoftware/mender-artifact/vendor/golang.org/x/text/LICENSE;md5=7998cb338f82d15c0eff93b7004d272a \
    file://src/github.com/mendersoftware/mender-artifact/vendor/golang.org/x/crypto/LICENSE;md5=7998cb338f82d15c0eff93b7004d272a \
    file://src/github.com/mendersoftware/mender-artifact/vendor/golang.org/x/time/LICENSE;md5=7998cb338f82d15c0eff93b7004d272a \
    file://src/github.com/mendersoftware/mender-artifact/vendor/golang.org/x/sync/LICENSE;md5=7998cb338f82d15c0eff93b7004d272a \
    file://src/github.com/mendersoftware/mender-artifact/vendor/google.golang.org/api/LICENSE;md5=a651bb3d8b1c412632e28823bb432b40 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/google.golang.org/api/internal/third_party/uritemplates/LICENSE;md5=4ee4feb2b545c2231749e5c54ace343e \
    file://src/github.com/mendersoftware/mender-artifact/vendor/google.golang.org/protobuf/LICENSE;md5=02d4002e9171d41a8fad93aa7faf3956 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/googleapis/gax-go/v2/LICENSE;md5=0dd48ae8103725bd7b401261520cdfbb \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/klauspost/compress/internal/snapref/LICENSE;md5=b8b79c7d4cda128290b98c6a21f9aac6 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/ulikunitz/xz/LICENSE;md5=3c82255323cf3d48815acdbf9068b715 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/google/uuid/LICENSE;md5=88073b6dd8ec00fe09da59e0b6dfded1 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/davecgh/go-spew/LICENSE;md5=c06795ed54b2a35ebeeb543cd3a73e56 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/decred/dcrd/dcrec/secp256k1/v4/LICENSE;md5=ada7190e9f09fd8b37ed52aff23bf178 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/stretchr/testify/LICENSE;md5=188f01994659f3c0d310612333d2a26f \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/urfave/cli/LICENSE;md5=75d9e324acacf92aca82397b81c225b0 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/sirupsen/logrus/LICENSE;md5=8dadfef729c08ec4e631c4f6fc5d43a0 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/klauspost/pgzip/LICENSE;md5=9ea3772c7ca56b5e8cbd5caf795588b5 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/cpuguy83/go-md2man/v2/LICENSE.md;md5=80794f9009df723bbc6fe19234c9f517 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/gopkg.in/yaml.v3/LICENSE;md5=3c91c17266710e16afdbb2b6d15c761c \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/mattn/go-isatty/LICENSE;md5=f509beadd5a11227c27b5d2ad6c9f2c6 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/klauspost/cpuid/v2/LICENSE;md5=00d6f962401947482d082858f7ba2ff3 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/mitchellh/go-homedir/LICENSE;md5=3f7765c3d4f58e1f84c4313cecf0f5bd \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/mitchellh/mapstructure/LICENSE;md5=3f7765c3d4f58e1f84c4313cecf0f5bd \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/ryanuber/go-glob/LICENSE;md5=d2c81b3028eb947731a58fb068c7dff4 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/cenkalti/backoff/v3/LICENSE;md5=1571d94433e3f3aa05267efd4dbea68b \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/klauspost/compress/zstd/internal/xxhash/LICENSE.txt;md5=802da049c92a99b4387d3f3d91b00fa9 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/Azure/azure-sdk-for-go/sdk/internal/LICENSE.txt;md5=a93cb0863fda8e7f177e09f6943951b4 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/Azure/azure-sdk-for-go/sdk/azidentity/LICENSE.txt;md5=a93cb0863fda8e7f177e09f6943951b4 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/Azure/azure-sdk-for-go/sdk/security/keyvault/internal/LICENSE.txt;md5=261d8686a7cf1ce9570cdc99746659f8 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/Azure/azure-sdk-for-go/sdk/security/keyvault/azkeys/LICENSE.txt;md5=261d8686a7cf1ce9570cdc99746659f8 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/Azure/azure-sdk-for-go/sdk/azcore/LICENSE.txt;md5=a93cb0863fda8e7f177e09f6943951b4 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/AzureAD/microsoft-authentication-library-for-go/LICENSE;md5=e74f78882cab57fd1cc4c5482b9a214a \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/goccy/go-json/LICENSE;md5=33a07164132d795872805bfc53f6097d \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/golang-jwt/jwt/v5/LICENSE;md5=a21b708d8b320c68979c44ac9dba9b0d \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/lestrrat-go/iter/LICENSE;md5=c1d03a9175ab48d85c699b2eb51ae56e \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/lestrrat-go/blackmagic/LICENSE;md5=8144a188cc06dee37074f74ffc17c90e \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/lestrrat-go/backoff/v2/LICENSE;md5=a40d3a08376a4204020182fb717f8960 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/lestrrat-go/httpcc/LICENSE;md5=c1d03a9175ab48d85c699b2eb51ae56e \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/lestrrat-go/option/LICENSE;md5=8144a188cc06dee37074f74ffc17c90e \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/lestrrat-go/jwx/LICENSE;md5=c94689f9bcf3eb6a81ad8f45767d5be3 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/hashicorp/go-secure-stdlib/strutil/LICENSE;md5=65d26fcc2f35ea6a181ac777e42db1ea \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/hashicorp/go-secure-stdlib/parseutil/LICENSE;md5=65d26fcc2f35ea6a181ac777e42db1ea \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/hashicorp/errwrap/LICENSE;md5=b278a92d2c1509760384428817710378 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/hashicorp/hcl/LICENSE;md5=b278a92d2c1509760384428817710378 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/hashicorp/go-cleanhttp/LICENSE;md5=65d26fcc2f35ea6a181ac777e42db1ea \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/hashicorp/go-rootcerts/LICENSE;md5=65d26fcc2f35ea6a181ac777e42db1ea \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/hashicorp/go-retryablehttp/LICENSE;md5=bffc21c92b5f3adcbbb06f8e0067e786 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/hashicorp/go-sockaddr/LICENSE;md5=9741c346eef56131163e13b9db1241b3 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/hashicorp/vault/api/LICENSE;md5=bffc21c92b5f3adcbbb06f8e0067e786 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/hashicorp/go-multierror/LICENSE;md5=d44fdeb607e2d2614db9464dbedd4094 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/felixge/httpsnoop/LICENSE.txt;md5=684da2bf3eed8fc8860e75ad84638225 \
"

DEPENDS += "xz openssl"
RDEPENDS:${PN} = "openssl"
