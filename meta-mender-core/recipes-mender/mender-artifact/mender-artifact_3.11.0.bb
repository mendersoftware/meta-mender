require mender-artifact.inc

################################################################################
#-------------------------------------------------------------------------------
# THINGS TO CONSIDER FOR EACH RELEASE:
# - SRC_URI (particularly "branch")
# - SRCREV
# - DEFAULT_PREFERENCE
#-------------------------------------------------------------------------------

SRC_URI = "git://github.com/mendersoftware/mender-artifact.git;protocol=https;branch=3.11.x"

# Tag: 3.11.0
SRCREV = "9d96b8beb5ebdec4eda1f5e9119d2f1335d516ac"

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
    file://src/github.com/mendersoftware/mender-artifact/LICENSE;md5=52b2497ce07650b825015e80ca7a5d40c360c04c530234ca6d950b0f98bca23a \
    file://src/github.com/mendersoftware/mender-artifact/vendor/cloud.google.com/go/compute/LICENSE;md5=cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/cloud.google.com/go/compute/metadata/LICENSE;md5=cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/cloud.google.com/go/iam/LICENSE;md5=cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/cloud.google.com/go/kms/LICENSE;md5=cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/cenkalti/backoff/v3/LICENSE;md5=5c0476add4c38b55d0ed5ac11b85e00c38f26e1caee20dfe3ab58190103d1fbc \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/cpuguy83/go-md2man/v2/LICENSE.md;md5=a55959c4e3e8917bfa857359bb641115336276a6cc97408fd8197e079fb18470 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/davecgh/go-spew/LICENSE;md5=1b93a317849ee09d3d7e4f1d20c2b78ddb230b4becb12d7c224c927b9d470251 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/go-jose/go-jose/v3/LICENSE;md5=cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/go-jose/go-jose/v3/json/LICENSE;md5=dd26a7abddd02e2d0aba97805b31f248ef7835d9e10da289b22e3b8ab78b324d \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/golang/groupcache/LICENSE;md5=73ba74dfaa520b49a401b5d21459a8523a146f3b7518a833eea5efa85130bf68 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/golang/protobuf/LICENSE;md5=8778a9fc1eaffb03ab873caae251df2d224f6b5502be8777d3cd573a4dd43903 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/google/go-cmp/LICENSE;md5=17b5d209ba8f9684257ecfcff87df6ceda6194143a8fbd074f29727cff6f0c40 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/google/s2a-go/LICENSE.md;md5=cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/googleapis/enterprise-certificate-proxy/LICENSE;md5=cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/googleapis/gax-go/v2/LICENSE;md5=b95218cd9607855a6536384c0262922b30a0c2bf56e4ced790240f3a3bac4722 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/hashicorp/errwrap/LICENSE;md5=bef1747eda88b9ed46e94830b0d978c3499dad5dfe38d364971760881901dadd \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/hashicorp/go-cleanhttp/LICENSE;md5=60222c28c1a7f6a92c7df98e5c5f4459e624e6e285e0b9b94467af5f6ab3343d \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/hashicorp/go-multierror/LICENSE;md5=a830016911a348a54e89bd54f2f8b0d8fffdeac20aecfba8e36ebbf38a03f5ff \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/hashicorp/go-retryablehttp/LICENSE;md5=60222c28c1a7f6a92c7df98e5c5f4459e624e6e285e0b9b94467af5f6ab3343d \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/hashicorp/go-rootcerts/LICENSE;md5=60222c28c1a7f6a92c7df98e5c5f4459e624e6e285e0b9b94467af5f6ab3343d \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/hashicorp/go-secure-stdlib/parseutil/LICENSE;md5=60222c28c1a7f6a92c7df98e5c5f4459e624e6e285e0b9b94467af5f6ab3343d \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/hashicorp/go-secure-stdlib/strutil/LICENSE;md5=60222c28c1a7f6a92c7df98e5c5f4459e624e6e285e0b9b94467af5f6ab3343d \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/hashicorp/go-sockaddr/LICENSE;md5=1f256ecad192880510e84ad60474eab7589218784b9a50bc7ceee34c2b91f1d5 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/hashicorp/hcl/LICENSE;md5=bef1747eda88b9ed46e94830b0d978c3499dad5dfe38d364971760881901dadd \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/hashicorp/vault/api/LICENSE;md5=d6b1a865f1c8c697d343bd4e0ce61025f91898486a1f00d727f32e8644af77d3 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/klauspost/compress/LICENSE;md5=0d9e582ee4bff57bf1189c9e514e6da7ce277f9cd3bc2d488b22fbb39a6d87cf \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/klauspost/compress/internal/snapref/LICENSE;md5=f69f157b0be75da373605dbc8bbf142e8924ee82d8f44f11bcaf351335bf98cf \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/klauspost/compress/zstd/internal/xxhash/LICENSE.txt;md5=f566a9f97bacdaf00d9f21dd991e81dc11201c4e016c86b470799429a1c9a79c \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/klauspost/cpuid/v2/LICENSE;md5=5d966570d7a442d4e969892860a914e542c97f262c873baee8f0aa48e1f40212 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/klauspost/pgzip/LICENSE;md5=7709cc030f078b17809884f92f33a2016944e1180312dc3f1371b02313d313ed \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/mattn/go-isatty/LICENSE;md5=08eab1118c80885fa1fa6a6dd7303f65a379fcb3733e063d20d1bbc2c76e6fa1 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/mendersoftware/openssl/LICENSE;md5=73ba74dfaa520b49a401b5d21459a8523a146f3b7518a833eea5efa85130bf68 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/mendersoftware/progressbar/LICENSE;md5=8f5d89b47d7a05a199b77b7e0f362dad391d451ebda4ef48ba11c50c071564c7 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/minio/sha256-simd/LICENSE;md5=cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/mitchellh/go-homedir/LICENSE;md5=22adc4abdece712a737573672f082fd61ac2b21df878efb87ffcff4354a07f26 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/mitchellh/mapstructure/LICENSE;md5=22adc4abdece712a737573672f082fd61ac2b21df878efb87ffcff4354a07f26 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/pkg/errors/LICENSE;md5=8d427fd87bc9579ea368fde3d49f9ca22eac857f91a9dec7e3004bdfab7dee86 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/pmezard/go-difflib/LICENSE;md5=2eb550be6801c1ea434feba53bf6d12e7c71c90253e0a9de4a4f46cf88b56477 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/remyoudompheng/go-liblzma/LICENSE;md5=87640bc4df2ceb1559f268a3db1ba859ab780f7ba5b1b4545173d4680a3d918b \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/russross/blackfriday/v2/LICENSE.txt;md5=75e1ca97a84a9da6051dee0114333388216f2c4a5a028296b882ff3d57274735 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/ryanuber/go-glob/LICENSE;md5=38049e50b486f5394e40b786388f4a006401996e46c7c1cd18925afe7c3b4e34 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/sirupsen/logrus/LICENSE;md5=51a0c9ec7f8b7634181b8d4c03e5b5d204ac21d6e72f46c313973424664b2e6b \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/stretchr/testify/LICENSE;md5=f8e536c1c7b695810427095dc85f5f80d44ff7c10535e8a9486cf393e2599189 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/github.com/urfave/cli/LICENSE;md5=2be6c75f36f3022ea015fea7b1b7135ce67d477ee721d0fc6c98678badb13b8b \
    file://src/github.com/mendersoftware/mender-artifact/vendor/go.opencensus.io/LICENSE;md5=58d1e17ffe5109a7ae296caafcadfdbe6a7d176f0bc4ab01e12a689b0499d8bd \
    file://src/github.com/mendersoftware/mender-artifact/vendor/golang.org/x/crypto/LICENSE;md5=2d36597f7117c38b006835ae7f537487207d8ec407aa9d9980794b2030cbc067 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/golang.org/x/crypto/LICENSE;md5=2d36597f7117c38b006835ae7f537487207d8ec407aa9d9980794b2030cbc067 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/golang.org/x/net/LICENSE;md5=2d36597f7117c38b006835ae7f537487207d8ec407aa9d9980794b2030cbc067 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/golang.org/x/oauth2/LICENSE;md5=2d36597f7117c38b006835ae7f537487207d8ec407aa9d9980794b2030cbc067 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/golang.org/x/sys/LICENSE;md5=2d36597f7117c38b006835ae7f537487207d8ec407aa9d9980794b2030cbc067 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/golang.org/x/text/LICENSE;md5=2d36597f7117c38b006835ae7f537487207d8ec407aa9d9980794b2030cbc067 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/golang.org/x/time/LICENSE;md5=2d36597f7117c38b006835ae7f537487207d8ec407aa9d9980794b2030cbc067 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/golang.org/x/time/LICENSE;md5=2d36597f7117c38b006835ae7f537487207d8ec407aa9d9980794b2030cbc067 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/google.golang.org/api/LICENSE;md5=110244b02140866ee37d17fa7449436a377ec3b85a481fbb208f4c87964382de \
    file://src/github.com/mendersoftware/mender-artifact/vendor/google.golang.org/api/internal/third_party/uritemplates/LICENSE;md5=fc0a2f71df4e8f047902da53d1f85301be43e0f360fc167057a2d04658ed2ba9 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/google.golang.org/appengine/LICENSE;md5=cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/google.golang.org/genproto/LICENSE;md5=cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/google.golang.org/genproto/googleapis/api/LICENSE;md5=cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/google.golang.org/genproto/googleapis/rpc/LICENSE;md5=cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/google.golang.org/grpc/LICENSE;md5=cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/google.golang.org/protobuf/LICENSE;md5=4835612df0098ca95f8e7d9e3bffcb02358d435dbb38057c844c99d7f725eb20 \
    file://src/github.com/mendersoftware/mender-artifact/vendor/gopkg.in/yaml.v3/LICENSE;md5=d18f6323b71b0b768bb5e9616e36da390fbd39369a81807cca352de4e4e6aa0b \
"

DEPENDS += "xz openssl"
RDEPENDS:${PN} = "openssl"
