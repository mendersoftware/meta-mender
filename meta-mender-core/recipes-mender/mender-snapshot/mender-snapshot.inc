DESCRIPTION = "Mender tool for creating golden-images from a given installation."
HOMEPAGE = "https://mender.io"

DEPENDS:append = " glib-2.0"
RDEPENDS:${PN} = "glib-2.0 mender-update (>= 4.0)"

B = "${WORKDIR}/build"

inherit go-mod
inherit go-ptest

GO_IMPORT = "github.com/mendersoftware/mender-snapshot"

# Prefer static linkage (golang's default)
GO_LINKSHARED = ""

# Set the version of mender-snapshot by passing it as an extra ldflag to go.bbclass
# This is equivalent to how it's set in the Makefile
GO_EXTRA_LDFLAGS:append = "-X github.com/mendersoftware/mender-snapshot/conf.Version=$(git describe --tags --dirty --exact-match 2>/dev/null || git rev-parse --short HEAD)"
